"""
بناء قاعدة معرفة السياسات (UAE policy KB) باستخدام خط الإدخال المرجعي من ITU.

Adapted from ITU AI for Good reference code:
  https://github.com/CrashingGuru/ITUAIReadiness  (simulation/server/knowledge/ingest.py)
  Copyright (c) 2026 Vishnu Ram OV — MIT License (see governance/ITU_REFERENCE_LICENSE.txt)

الأجزاء المأخوذة كما هي تقريباً: parse_file / _parse_pdf / chunk_text (256 كلمة، تداخل 30) /
infer_source_type / infer_country / build_metadata / ingest_framework_definitions / بنية المجلدات = فئات.
التعديلات (موثّقة للتقرير التقني):
  1. نموذج التضمين bge-m3 بدل nomic-embed-text لأنه بيدعم العربي (قابل للتغيير: EMBED_MODEL=nomic-embed-text).
  2. التقطيع لكل صفحة PDF لوحدها + حفظ رقم الصفحة ورقم المادة (Article/المادة) بالـ metadata
     عشان الاستشهادات بالسجل تكون قابلة للتتبع.
  3. ملف manifest.yaml بيعطي لكل وثيقة: العنوان، الجهة المصدرة، السنة، اللغة، الرابط الرسمي.
  4. أنماط إضافية لدولة الإمارات والجهات التعليمية (MoE, KHDA, ADEK, TDRA, UAE Data Office).
  5. معرّفات ثابتة للقطع (doc_id:page:index) بدل uuid عشان السجل يقدر يرجع لنفس القطعة.
  6. تصدير قاعدة المعرفة كملف JSONL مفتوح (policy_kb_export.jsonl) لتسليمه لمختبر ITU.

الاستخدام:
  python -m governance.itu_ingest            # بناء/إعادة بناء kb_policy_uae و kb_framework
  python -m governance.itu_ingest --list     # عرض الوثائق الموجودة والناقصة بدون تضمين
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml

from . import config as C
from . import retrieval

SUPPORTED = {".pdf", ".txt", ".md", ".csv", ".html", ".htm"}
CHUNK_SIZE, CHUNK_OVERLAP = 256, 30          # نفس إعدادات ITU (settings.chunk_size / chunk_overlap)

# ---------------------------------------------------------------- metadata inference (ITU + UAE patterns)
_SOURCE_TYPE_PATTERNS = [
    (r"(?i)ITU|Y\.3172|AI4G|sandbox|readiness", "standards_document"),
    (r"(?i)UNESCO|OECD|UNICEF|Oxford|UNCTAD|CCIA|Turing", "international_org_report"),
    (r"(?i)law|decree|pdpl|regulation|act\b|قانون|مرسوم", "law_regulation"),
    (r"(?i)national.*(strategy|plan)|NAIS|SDAIA|NSDAI|strategy_2031|استراتيجية", "national_strategy"),
    (r"(?i)charter|ethic|principle|guideline|guidance|policy|governance|ميثاق|إرشاد|سياسة", "policy_document"),
]
_COUNTRY_PATTERNS = [
    (r"(?i)uae|emirat|dubai|abu.?dhabi|khda|adek|tdra|moe_uae|الإمارات|دبي|ابوظبي", "United Arab Emirates"),
    (r"(?i)saudi|SDAIA|NSDAI", "Saudi Arabia"),
    (r"(?i)singapore|NAIS", "Singapore"),
    (r"(?i)\bEU\b|EU_|european", "European Union"),
    (r"(?i)unesco|oecd|unicef|itu|un_", "global"),
]


def infer_source_type(name):
    for p, t in _SOURCE_TYPE_PATTERNS:
        if re.search(p, name):
            return t
    return "international_org_report"


def infer_country(name):
    for p, c in _COUNTRY_PATTERNS:
        if re.search(p, name):
            return c
    return "global"


# ---------------------------------------------------------------- parsing (ITU parse_file, page-aware)
def _strip_html(html):
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        for t in soup(["script", "style", "nav", "header", "footer", "aside", "form", "noscript", "svg"]):
            t.decompose()
        main = soup.select_one("main, article, [role=main], #content, .content") or soup.body or soup
        return main.get_text("\n", strip=True)
    except ImportError:                                  # نفس fallback تبع ITU
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def _parse_pdf_pages(path):
    """PyMuPDF أول (نفس ITU)، بعدين pypdf كبديل. بيرجع [(رقم الصفحة، النص)]."""
    try:
        try:
            import pymupdf as fitz          # pymupdf >= 1.24 / 2.x
        except ImportError:
            import fitz                     # الأسماء القديمة
        with fitz.open(str(path)) as doc:
            return [(i + 1, p.get_text()) for i, p in enumerate(doc)]
    except ImportError:
        pass
    try:
        from pypdf import PdfReader
        return [(i + 1, p.extract_text() or "") for i, p in enumerate(PdfReader(str(path)).pages)]
    except ImportError:
        raise SystemExit("لقراءة ملفات PDF ثبّت: pip install pymupdf")


_AR = "\u0621-\u064A"
_AR_WORD_FIX = {"يف": "في", "ويف": "وفي", "ميكن": "يمكن", "وميكن": "ويمكن", "كام": "كما", "وكام": "وكما"}


_LAM_ALEF = re.compile(r"(?<=[اأإآ])([اأإآ])ل")
_BROKEN = re.compile(f"(?<![{_AR}])(عىل|إىل|اىل|يف)(?![{_AR}])|(?<![{_AR}])[وفب]?امل[{_AR}]|(?<![{_AR}])[وفب]?اال[{_AR}]")


def fix_arabic_pdf_text(t):
    """إصلاح نص عربي مستخرج من PDF: الحروف المركّبة (ligatures) بتطلع أحياناً مقلوبة أو بأشكال العرض.
    مثال: "املتحكم" → "المتحكم"، "عىل" → "على"، "باالشتراك" → "بالاشتراك"، "ﺣﻮادث" → "حوادث".
    التصحيحات القوية بتنطبق بس على صفحة عليها علامات خلل واضحة (عشان ما نخرّب كلمات صحيحة زي "كاملة")."""
    import unicodedata
    t = unicodedata.normalize("NFKC", t)
    t = re.sub("[\u202a-\u202e]", "", t)                                   # علامات اتجاه مخفية
    # "لا/لأ/لإ/لآ" المقلوبة بعد ألف: "اإلمارات" → "الإمارات"، "المجاالت" → "المجالات". (ألف + ألف/همزة + لام
    # ما بتيجي بكلمة عربية سليمة، فالتصحيح آمن على كل الصفحات، ومرتين للانقلاب المزدوج: "اآلالت" → "الآلات")
    for _ in range(3):
        n = _LAM_ALEF.sub(lambda m: "ل" + m.group(1), t)
        if n == t:
            break
        t = n
    if len(_BROKEN.findall(t)) < 3:                                       # الصفحة سليمة: بس التطبيع
        return t
    t = re.sub(f"ى([{_AR}])(?=[^{_AR}]|$)", r"\1ى", t)                      # "ى" ما بتيجي إلا بآخر الكلمة
    t = re.sub(f"(?<![{_AR}])([وفب]?)امل(?=[{_AR}])", lambda m: m.group(1) + "الم", t)
    t = re.sub(f"(?<![{_AR}])([وفب]?)اال(?=[{_AR}])", lambda m: m.group(1) + "الا", t)
    t = re.sub(f"(?<![{_AR}])({'|'.join(_AR_WORD_FIX)})(?![{_AR}])", lambda m: _AR_WORD_FIX[m.group(1)], t)
    return t


def parse_file_pages(path: Path):
    s = path.suffix.lower()
    if s == ".pdf":
        return [(n, fix_arabic_pdf_text(t)) for n, t in _parse_pdf_pages(path)]
    raw = path.read_text(encoding="utf-8", errors="replace")
    if s in (".html", ".htm"):
        raw = _strip_html(raw)
    return [(None, raw)]


# ---------------------------------------------------------------- chunking (ITU chunk_text, verbatim logic)
def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP, max_chars=2000):
    if not text or not text.strip():
        return []
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks, current = [], []
    for para in paragraphs:
        for word in para.split():
            current.append(word)
            if len(current) >= chunk_size:
                chunks.append(" ".join(current))
                current = current[-overlap:] if overlap > 0 else []
    if current:
        last = " ".join(current)
        if len(current) > 20 or not chunks:
            chunks.append(last)
        elif chunks:
            chunks[-1] = chunks[-1] + " " + last
    safe = []
    for ch in chunks:
        if len(ch) <= max_chars:
            safe.append(ch)
        else:
            safe.extend(p.strip() for p in (ch[i:i + max_chars] for i in range(0, len(ch), max_chars)) if p.strip())
    return safe


_AR_ORD = {"الأولى": "1", "الاولى": "1", "الثانية": "2", "الثالثة": "3", "الرابعة": "4", "الخامسة": "5", "السادسة": "6",
           "السابعة": "7", "الثامنة": "8", "التاسعة": "9", "العاشرة": "10"}
_ARTICLE = re.compile(r"(?:\bArticle\s*\(?\s*(\d{1,3})\s*\)?|المادة\s*\(?\s*([0-9٠-٩]{1,3}|" + "|".join(_AR_ORD) + r")\s*\)?)", re.I)
# عنوان مادة = بأول السطر (مش إشارة لمادة ثانية بنص الفقرة مثل "وفقاً للمادة 22")
_ARTICLE_HEAD = re.compile(r"(?m)^\s*(?:\bArticle\s*\(?\s*(\d{1,3})\s*\)?|المادة\s*\(?\s*([0-9٠-٩]{1,3}|" + "|".join(_AR_ORD) + r")\s*\)?)", re.I)
_AR_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def _art_value(m):
    v = (m.group(1) or m.group(2) or "").strip()
    return _AR_ORD.get(v, v.translate(_AR_DIGITS))


def _article_in(text):
    m = _ARTICLE.search(text)
    return _art_value(m) if m else None


def _article_heads(text):
    """[(رقم الكلمة اللي بيبلش فيها العنوان، رقم المادة)] بالترتيب."""
    return [(len(text[:m.start()].split()), _art_value(m)) for m in _ARTICLE_HEAD.finditer(text)]


def _lang(text):
    letters = [c for c in text if c.isalpha()]
    return "ar" if sum("؀" <= c <= "ۿ" for c in letters) / max(len(letters), 1) > 0.4 else "en"


# ---------------------------------------------------------------- manifest
def load_manifest():
    if not C.POLICY_MANIFEST.exists():
        return {}
    data = yaml.safe_load(C.POLICY_MANIFEST.read_text(encoding="utf-8")) or {}
    out = {}
    for d in data.get("documents", []):
        if d.get("file"):      # المفتاح بدون امتداد: الامتداد بيتحدد وقت التنزيل (.pdf/.html)
            out[_key(d["file"])] = d
    return out


def _key(rel):
    p = Path(rel)
    return (p.parent / p.stem).as_posix() if p.suffix.lower() in SUPPORTED else p.as_posix()


def discover():
    """كل الملفات بمجلدات الفئات + بيانات manifest. بيرجع (موجود، ناقص)."""
    manifest = load_manifest()
    found, seen = [], set()
    # المجلدات اللي بتبلش بـ _ أو . (زي _to_delete) مش فئات. الترتيب بالأحرف الصغيرة عشان يكون نفسه على Windows وLinux
    for cat_dir in sorted((p for p in C.POLICY_DIR.iterdir() if p.is_dir() and not p.name.startswith(("_", "."))),
                          key=lambda p: p.name.lower()):
        # PDF أول: إذا في نسخة PDF وHTML لنفس الوثيقة (أو صفحة خطأ HTML) بناخد الـ PDF
        for f in sorted(cat_dir.rglob("*"), key=lambda f: (f.parent.as_posix(), f.stem, f.suffix.lower() != ".pdf")):
            if not f.is_file() or f.suffix.lower() not in SUPPORTED or f.name.lower() in ("inputs.md", "readme.md"):
                continue
            rel = _key(f.relative_to(C.POLICY_DIR).as_posix())
            if rel in seen:            # نفس الوثيقة بصيغتين (pdf + html): ناخد وحدة بس
                continue
            seen.add(rel)
            m = dict(manifest.get(rel, {}))
            m.setdefault("id", re.sub(r"[^\w]+", "_", f.stem).strip("_").lower())
            m.setdefault("title", f.stem.replace("_", " "))
            m.setdefault("category", cat_dir.name)
            found.append((f, m))
    missing = [d for rel, d in manifest.items() if rel not in seen]
    # نفس الملف محفوظ باسمين (صار معنا: قانون سلامة الطفل انحفظ باسم وثيقة اليونسكو) => بنتجاهل النسخة الثانية
    import hashlib
    by_hash, unique = {}, []
    for f, m in found:
        h = hashlib.md5(f.read_bytes()).hexdigest()
        if h in by_hash:
            print(f"  ⚠️ {f.name} هو نفس ملف {by_hash[h].name} بالضبط — تم تجاهله. نزّل الوثيقة الصحيحة واحفظها بهالاسم.")
            missing.append(m)
            continue
        by_hash[h] = f
        unique.append((f, m))
    return unique, missing


def build_metadata(path, doc, page, idx, total, article, text):
    """build_metadata تبع ITU + حقول التتبع."""
    name = path.name + " " + str(doc.get("title", ""))
    return {k: v for k, v in {
        "source_file": path.name, "source_type": doc.get("doc_type") or infer_source_type(name),
        "country": doc.get("jurisdiction") or infer_country(name), "document_category": doc["category"],
        "category": doc["category"], "doc_id": doc["id"], "title": str(doc.get("title", ""))[:300],
        "issuer": str(doc.get("issuer", "")), "year": str(doc.get("year", "")), "lang": doc.get("lang") or _lang(text),
        "url": str(doc.get("url", "")), "page": page if page is not None else -1, "article": article or "",
        "binding_scope": doc.get("binding_scope") or _scope(doc["category"]), "license": str(doc.get("license", "")),
        "chunk_index": idx, "total_chunks": total,
        "ingested_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }.items() if v is not None}


def _scope(category):
    """مدى الإلزام: اتحادي/إمارة (ملزم لمدارس الإمارات)، منطقة حرة، دولي (للمقارنة)، معيار."""
    return {"UAE_FreeZone": "free_zone", "International_Benchmarks": "international",
            "ITU_Standards": "standard"}.get(category, "federal" if category.startswith("UAE") else "international")


def ingest_document(path, doc):
    pages = parse_file_pages(path)
    items, article = [], None
    for page, text in pages:
        words = text.split()
        heads = _article_heads(text)
        pos = 0
        for ch in chunk_text(text):
            cw = ch.split()
            # مكان القطعة بالصفحة (القطع متتالية مع تداخل): بندوّر على أول كلمات القطعة
            for i in range(max(0, pos - 40), len(words)):
                if words[i:i + min(6, len(cw))] == cw[:min(6, len(cw))]:
                    pos = i
                    break
            before = [a for w, a in heads if w <= pos]
            inside = [a for w, a in heads if pos < w < pos + len(cw)]
            article = before[-1] if before else article     # المادة السارية ببداية القطعة
            items.append((page, ch, article or (inside[0] if inside else None)))
    total = len(items)
    ids, texts, metas = [], [], []
    for i, (page, ch, art) in enumerate(items):
        ids.append(f"{doc['id']}:{page if page is not None else 0}:{i}")
        texts.append(ch)
        metas.append(build_metadata(path, doc, page, i, total, art, ch))
    return ids, texts, metas


def ingest_framework_definitions():
    """من ITU: كل dimension و factor بإطار AI Readiness 2.0 بيصير مستند بمجموعة kb_framework."""
    if not C.FRAMEWORK_JSON.exists():
        return 0
    data = json.loads(C.FRAMEWORK_JSON.read_text(encoding="utf-8"))
    texts, metas, ids = [], [], []
    for dim in data["dimensions"]:
        metrics = "\n".join(f"- {m['name']}: {m['description']}" for m in dim["metrics"])
        texts.append(f"Dimension {dim['id']}: {dim['name']}\n\n{dim['description']}\n\n"
                     f"Mapped Factors: {', '.join(dim['mapped_factors'])}\n\nMetrics:\n{metrics}")
        metas.append({"dimension_id": str(dim["id"]), "dimension_name": dim["name"], "short_name": dim["short_name"],
                      "source_type": "framework_definition", "entity_type": "dimension",
                      "factors": ",".join(dim["mapped_factors"]), "title": "ITU AI Readiness Framework 2.0",
                      "doc_id": "itu_ai_readiness_framework", "category": "ITU_Standards"})
        ids.append(f"dim:{dim['id']}")
    for f in data["factors"]:
        texts.append(f"Factor: {f['name']}\n\n{f['description']}")
        metas.append({"factor_id": f["id"], "factor_name": f["name"], "source_type": "framework_definition",
                      "entity_type": "factor", "title": "ITU AI Readiness Framework 2.0",
                      "doc_id": "itu_ai_readiness_framework", "category": "ITU_Standards"})
        ids.append(f"factor:{f['id']}")
    col = retrieval.reset_collection(C.FRAMEWORK_COLLECTION)
    col.add(ids=ids, documents=texts, metadatas=metas, embeddings=retrieval.embed_many(texts))
    return len(texts)


def _existing(col):
    """كل المقاطع الموجودة بالمجموعة: {doc_id: عدد المقاطع} + صفوف التصدير."""
    got = col.get(include=["documents", "metadatas"])
    rows = [{"id": i, "text": t, "metadata": m} for i, t, m in zip(got["ids"], got["documents"], got["metadatas"])]
    counts = {}
    for r in rows:
        counts[r["metadata"].get("doc_id")] = counts.get(r["metadata"].get("doc_id"), 0) + 1
    return counts, rows


def main():
    ap = argparse.ArgumentParser(description="Build the UAE policy knowledge base (ITU reference pipeline)")
    ap.add_argument("--list", action="store_true", help="اعرض الوثائق بدون بناء")
    ap.add_argument("--add", action="store_true", help="أضف الوثائق الجديدة بس (بدون إعادة بناء الموجود)")
    ap.add_argument("--redo", default="", help="أعد إدخال وثائق معيّنة بالـ id، مفصولة بفواصل (مع --add ضمنياً)")
    a = ap.parse_args()
    found, missing = discover()
    print(f"وثائق موجودة: {len(found)} | ناقصة من manifest: {len(missing)}")
    for f, d in found:
        print(f"  ✓ [{d['category']}] {f.name}")
    for d in missing:
        print(f"  ✗ [{d.get('category')}] {d.get('file')}  ← نزّلها من: {d.get('url')}")
    if a.list:
        return
    redo = {x.strip() for x in a.redo.split(",") if x.strip()}
    if redo:
        a.add = True
        col = retrieval.collection(C.POLICY_COLLECTION, create=True)
        for doc_id in redo:
            col.delete(where={"doc_id": doc_id})
            print(f"  ↺ حذفنا مقاطع {doc_id} القديمة")
    if a.add:
        col = retrieval.collection(C.POLICY_COLLECTION, create=True)
        have, _ = _existing(col)
        todo = [(f, d) for f, d in found if d["id"] not in have]
        print(f"\n--add: {len(have)} وثيقة موجودة بالقاعدة، رح نضيف {len(todo)} جديدة")
    else:
        col = retrieval.reset_collection(C.POLICY_COLLECTION)
        todo = found
    for f, d in todo:
        ids, texts, metas = ingest_document(f, d)
        if not texts:
            print(f"  !! ما انستخرج نص من {f.name} (ممكن يكون PDF مصوّر)")
            continue
        emb_in = [f"{d.get('title', '')} — {d['category']}\n{t}" for t in texts]
        print(f"  .. {f.name}: {len(texts)} chunks", flush=True)
        for i in range(0, len(texts), 64):
            col.add(ids=ids[i:i + 64], documents=texts[i:i + 64], metadatas=metas[i:i + 64],
                    embeddings=retrieval.embed_many(emb_in[i:i + 64]))
            print(f"     {f.name}: {min(i + 64, len(texts))}/{len(texts)}", end="\r", flush=True)
        print(f"\r  => {f.name}: {len(texts)} chunks          ")
    counts, export = _existing(col)
    with open(C.POLICY_EXPORT, "w", encoding="utf-8") as fh:
        for row in export:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    try:
        fw = retrieval.collection(C.FRAMEWORK_COLLECTION).count() if a.add else 0
    except Exception:
        fw = 0
    if not fw:
        fw = ingest_framework_definitions()
    summary = []
    for f, d in found:
        meta = next((r["metadata"] for r in export if r["metadata"].get("doc_id") == d["id"]), {})
        summary.append({"doc_id": d["id"], "file": f.name, "category": d["category"], "lang": meta.get("lang"),
                        "chunks": counts.get(d["id"], 0), "url": d.get("url", "")})
    (C.KB_DIR / "policy_kb_summary.json").write_text(json.dumps({
        "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "embed_model": C.EMBED_MODEL,
        "pipeline": "ITU AI for Good reference ingest (adapted, MIT)", "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP, "policy_chunks": len(export), "framework_docs": fw,
        "documents": summary, "missing": [d.get("file") for d in missing]}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nkb_policy_uae: {len(export)} chunks | kb_framework: {fw} | export: {C.POLICY_EXPORT.name}")


if __name__ == "__main__":
    main()
