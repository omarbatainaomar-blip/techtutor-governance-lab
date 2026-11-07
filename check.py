"""فحص سريع:
  python check.py --stats                      # كم قطعة لكل مصدر
  python check.py "شو الفرق بين TCP و UDP؟"     # أقرب النتائج + المسافات (لمعايرة MAX_DIST)
  python check.py "what is a primary key" --topic databases
"""
import argparse, os, sqlite3

ap = argparse.ArgumentParser()
ap.add_argument("question", nargs="?")
ap.add_argument("--topic", default="all")
ap.add_argument("--stats", action="store_true")
a = ap.parse_args()

if a.stats:
    con = sqlite3.connect(os.getenv("KB_DB", "knowledge_base/education_technology_knowledge_base.sqlite"))
    print(f"{'source':8} {'status':22} {'chunks':>7}  title")
    for sid, title, st, n in con.execute(
            "select s.source_id,s.title,s.status,(select count(*) from knowledge_chunks c where c.source_id=s.source_id) "
            "from sources s order by 1"):
        print(f"{sid:8} {st:22} {n:7}  {title}")
if a.question:
    from rag import retrieve, MAX_DIST
    print(f"(MAX_DIST = {MAX_DIST})")
    for h in retrieve(a.question, a.topic, k=8):
        m = h["meta"]
        flag = "ok " if h["dist"] <= MAX_DIST else "cut"
        print(f"{flag} {h['dist']:.3f}  {m['source_id']}  {m['heading'][:50]}\n        {h['text'][:110]!r}")
