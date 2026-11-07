"""
جمع المصادر وتقطيعها وتعبئة جدول knowledge_chunks بنفس الـ sqlite.
  python ingest.py --max-pages 3          # تجربة سريعة لكل المصادر
  python ingest.py --only SRC008          # مصدر واحد
  python ingest.py                        # كله
الزاحف بيحترم robots.txt وبيستنى ثانية بين كل طلب.
"""
import argparse, collections, datetime, hashlib, re, sqlite3, time
import urllib.parse, urllib.robotparser
import requests, yaml
from bs4 import BeautifulSoup

DB = "knowledge_base/education_technology_knowledge_base.sqlite"
UA = "TechTutorBot/0.1 (educational competition project; polite crawler)"
DELAY = 1.0
CHUNK_WORDS = 220
MIN_WORDS = 25
BLOCK = ["p", "li", "pre", "dt", "dd", "blockquote", "td"]
SKIP_EXT = re.compile(r"\.(pdf|zip|png|jpe?g|gif|svg|css|js|xml|json|mp4|epub)(\?|$)", re.I)


# ---------- DB ----------
def migrate(con):
    cols = {r[1] for r in con.execute("pragma table_info(knowledge_chunks)")}
    for c in ("page_url", "topics"):
        if c not in cols:
            con.execute(f"alter table knowledge_chunks add column {c} TEXT")
    con.commit()


def ensure_source(con, sid, cfg):
    if con.execute("select 1 from sources where source_id=?", (sid,)).fetchone():
        return
    con.execute(
        "insert into sources(source_id,title,domain,source_type,url,description,license_notes,access_method,status,added_on)"
        " values(?,?,?,?,?,?,?,?,?,?)",
        (sid, cfg["title"], cfg["domain"], cfg["source_type"], cfg["url"], cfg["description"],
         cfg.get("license_notes"), cfg.get("access_method"), "catalogued_not_ingested", now()))
    con.execute("insert into ingestion_jobs(source_id,status,method) values(?,?,?)",
                (sid, "pending", cfg.get("access_method")))
    con.commit()


def now():
    return datetime.datetime.now().isoformat(timespec="seconds")


# ---------- crawling ----------
_robots = {}


def allowed(url):
    p = urllib.parse.urlparse(url)
    base = f"{p.scheme}://{p.netloc}"
    if base not in _robots:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(base + "/robots.txt")
        try:
            rp.read()
        except Exception:
            rp = None
        _robots[base] = rp
    rp = _robots[base]
    return True if rp is None else rp.can_fetch(UA, url)


def extract(html, url):
    soup = BeautifulSoup(html, "html.parser")
    links = [urllib.parse.urljoin(url, a["href"]).split("#")[0] for a in soup.find_all("a", href=True)]
    title = (soup.title.string or url).strip() if soup.title else url
    for t in soup(["script", "style", "nav", "header", "footer", "aside", "form", "noscript", "svg"]):
        t.decompose()
    main = soup.select_one("main, article, [role=main], #content, .content") or soup.body or soup
    sections, heading, paras = [], title, []
    for el in main.find_all(["h1", "h2", "h3", "h4"] + BLOCK):
        if el.name[0] == "h" and len(el.name) == 2:
            if paras:
                sections.append((heading, paras))
            heading, paras = el.get_text(" ", strip=True) or heading, []
        else:
            if el.find(BLOCK):          # حاوية: ناخد أوراقها بس
                continue
            txt = el.get_text("\n" if el.name == "pre" else " ", strip=True)
            if txt:
                paras.append(txt)
    if paras:
        sections.append((heading, paras))
    return {"url": url, "title": title, "sections": sections, "links": links}


def crawl(cfg, limit):
    queue = collections.deque(cfg["start_urls"])
    seen, n = set(queue), 0
    while queue and n < limit:
        url = queue.popleft()
        if not allowed(url):
            print("  robots.txt blocks:", url)
            continue
        try:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=30)
        except Exception as e:
            print("  error:", url, e)
            continue
        time.sleep(DELAY)
        if r.status_code != 200 or "text/html" not in r.headers.get("content-type", ""):
            continue
        page = extract(r.text, url)
        n += 1
        print(f"  [{n}] {url}")
        yield page
        for l in page["links"]:
            if (l.startswith(cfg["prefix"]) and l not in seen and not SKIP_EXT.search(l)
                    and not any(x in l for x in cfg.get("exclude", []))):
                seen.add(l)
                queue.append(l)


# ---------- wikipedia ----------
def wiki_fetch(lang, title):
    r = requests.get(f"https://{lang}.wikipedia.org/w/api.php", headers={"User-Agent": UA}, timeout=30, params={
        "action": "query", "format": "json", "redirects": 1, "prop": "extracts|langlinks|info",
        "explaintext": 1, "exsectionformat": "wiki", "lllang": "ar", "inprop": "url", "titles": title})
    r.raise_for_status()
    p = next(iter(r.json()["query"]["pages"].values()))
    if "missing" in p or not p.get("extract"):
        return None
    ar = next((l["*"] for l in p.get("langlinks", []) if l["lang"] == "ar"), None)
    sections, heading, paras = [], p["title"], []
    for block in re.split(r"\n{2,}", p["extract"]):
        m = re.fullmatch(r"=+\s*(.+?)\s*=+", block.strip())
        if m:
            if paras:
                sections.append((heading, paras))
            heading, paras = m.group(1), []
            if heading.lower() in ("see also", "references", "external links", "further reading", "notes",
                                   "انظر أيضا", "مراجع", "وصلات خارجية", "مصادر", "هوامش"):
                heading = None
                break
        elif block.strip():
            paras.append(block.strip())
    if paras and heading:
        sections.append((heading, paras))
    return {"url": p["fullurl"], "title": p["title"], "sections": sections, "ar_title": ar}


def wikipedia_pages(cfg, limit):
    n = 0
    for topic, titles in cfg["titles"].items():
        for t in titles:
            if n >= limit:
                return
            try:
                en = wiki_fetch("en", t)
                if not en:
                    print("  missing:", t)
                    continue
                en.update(lang="en", topics=[topic])
                n += 1
                print(f"  [{n}] {en['url']}")
                yield en
                if en["ar_title"]:
                    ar = wiki_fetch("ar", en["ar_title"])
                    if ar:
                        ar.update(lang="ar", topics=[topic])
                        yield ar
            except Exception as e:
                print("  error:", t, e)
            time.sleep(0.3)



# ---------- local markdown notes ----------
def _doc_lang(text):
    letters = [c for c in text if c.isalpha()]
    return "ar" if sum("\u0600" <= c <= "\u06ff" for c in letters) / max(len(letters), 1) > 0.4 else "en"


def local_pages(cfg, limit):
    """كل ملف .md ممكن يحتوي أكثر من مستند. كل مستند بيبدأ بسطر تعليق:
       <!-- id: اسم_المستند; topics: a,b -->   ثم عنوان رئيسي  # العنوان
       الأقسام ## و### بتصير headings للقطع. الكود المحاط بـ ``` بيبقى قطعة وحدة."""
    import pathlib
    n = 0
    for f in sorted(pathlib.Path(cfg["path"]).glob("*.md")):
        docs, cur = [], None
        pending = {"id": f.stem, "topics": cfg.get("topics", [])}
        in_code, code = False, []

        def start(title):
            nonlocal cur
            cur = {"id": pending["id"], "topics": pending["topics"], "title": title,
                   "sections": [], "heading": title, "paras": [], "text": []}
            docs.append(cur)

        def close_section():
            if cur and cur["paras"]:
                cur["sections"].append((cur["heading"], cur["paras"]))
                cur["paras"] = []

        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("```"):
                code.append(line.rstrip())
                if in_code and cur:
                    cur["paras"].append("\n".join(code))
                    cur["text"].append("\n".join(code))
                    code = []
                in_code = not in_code
                continue
            if in_code:
                code.append(line.rstrip())
                continue
            m = re.match(r"<!--(.*?)-->", line.strip())
            if m:
                body = m.group(1)
                t = re.search(r"topics:\s*([\w,\s]+?)\s*(?:;|$)", body)
                i = re.search(r"id:\s*([\w\-]+)", body)
                if t:
                    pending["topics"] = [x.strip() for x in t.group(1).split(",") if x.strip()]
                if i:
                    pending["id"] = i.group(1)
                continue
            if not line.strip():
                continue
            if line.startswith("# "):
                close_section()
                start(line[2:].strip())
                continue
            if cur is None:
                start(f.stem)
            cur["text"].append(line)
            if line.startswith("#"):
                close_section()
                cur["heading"] = line.lstrip("# ").strip()
            else:
                cur["paras"].append(line.strip())
        close_section()
        for d in docs:
            if n >= limit:
                return
            n += 1
            print(f"  [{n}] {f.name} :: {d['id']}")
            yield {"url": f"claude_notes/{f.name}#{d['id']}", "title": d["title"], "sections": d["sections"],
                   "lang": _doc_lang(" ".join(d["text"])), "topics": d["topics"]}


# ---------- chunking ----------
def chunk_paras(paras):
    cur, words, out = [], 0, []
    for p in paras:
        w = len(p.split())
        if cur and words + w > CHUNK_WORDS:
            out.append("\n".join(cur))
            cur, words = [], 0
        if w > CHUNK_WORDS * 2:                       # فقرة/كود طويل
            lines, buf, bw = p.split("\n"), [], 0
            for ln in lines:
                lw = len(ln.split())
                if buf and bw + lw > CHUNK_WORDS:
                    out.append("\n".join(buf)); buf, bw = [], 0
                buf.append(ln); bw += lw
            if buf:
                cur, words = buf, bw
            continue
        cur.append(p)
        words += w
    if cur:
        out.append("\n".join(cur))
    # دمج الذيل الصغير بالقطعة السابقة
    if len(out) > 1 and len(out[-1].split()) < MIN_WORDS:
        out[-2] += "\n" + out.pop()
    return [c for c in out if len(c.split()) >= MIN_WORDS]


# ---------- main ----------
def ingest_source(con, sid, cfg, max_pages):
    limit = max_pages or cfg.get("max_pages", 1000 if cfg.get("kind") == "local" else 50)
    kind = cfg.get("kind")
    pages = (wikipedia_pages(cfg, limit) if kind == "wikipedia"
             else local_pages(cfg, limit) if kind == "local" else crawl(cfg, limit))
    # بنجمع القطع الجديدة أول؛ ما بنحذف القديمة إلا إذا الجلب نجح (عشان فشل الشبكة ما يمسح البيانات)
    idx, npages, hashes, rows = 0, 0, set(), []
    for pg in pages:
        npages += 1
        lang = pg.get("lang", cfg.get("lang", "en"))
        topics = ",".join(pg.get("topics") or cfg["topics"])
        for heading, paras in pg["sections"]:
            for c in chunk_paras(paras):
                h = hashlib.sha1(c.encode("utf-8")).hexdigest()
                if h in hashes:
                    continue
                hashes.add(h)
                rows.append((sid, idx, heading, c, h, lang, now(), pg["url"], topics))
                idx += 1
    if rows:
        con.execute("delete from knowledge_chunks where source_id=?", (sid,))
        con.executemany(
            "insert into knowledge_chunks(source_id,chunk_index,heading,content,content_hash,language,ingested_on,page_url,topics)"
            " values(?,?,?,?,?,?,?,?,?)", rows)
    else:
        print(f"  !! {sid}: ما انجاب أي محتوى، القطع القديمة بقيت زي ما هي")
    status = "ingested" if idx else "failed_no_content"
    con.execute("update sources set status=? where source_id=?", (status, sid))
    con.execute("update ingestion_jobs set status=?, last_attempt=?, notes=? where source_id=?",
                ("done" if idx else "failed", now(), f"{npages} pages, {idx} chunks", sid))
    con.commit()
    print(f"  => {sid}: {npages} pages, {idx} chunks ({status})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="مثال: SRC008")
    ap.add_argument("--max-pages", type=int, default=0, help="حد أعلى للصفحات لكل مصدر (للتجربة)")
    ap.add_argument("--config", default="sources.yaml")
    ap.add_argument("--db", default=DB)
    a = ap.parse_args()
    cfgs = yaml.safe_load(open(a.config, encoding="utf-8"))
    con = sqlite3.connect(a.db)
    migrate(con)
    for sid, cfg in cfgs.items():
        if a.only and sid != a.only:
            continue
        if cfg.get("enabled") is False:
            print(f"skip {sid} (disabled)")
            continue
        if "title" in cfg:
            ensure_source(con, sid, cfg)
        print(f"== {sid}")
        ingest_source(con, sid, cfg, a.max_pages)


if __name__ == "__main__":
    main()
