"""
تقييم البوت على eval/questions.json
  python eval.py                 # تقييم الاسترجاع (retrieval) فقط: سريع وما بيحتاج نموذج دردشة
  python eval.py --generate      # بيشغّل النموذج كمان ويفحص الأجوبة (أبطأ)
  python eval.py --lang ar       # بس الأسئلة العربية
بيطبع: نسبة نجاح الاسترجاع، نسبة رفض الأسئلة خارج النطاق، واقتراح لقيمة MAX_DIST.
"""
import argparse, json, statistics
from rag import retrieve, answer, MAX_DIST, TOP_K, NOT_FOUND

ap = argparse.ArgumentParser()
ap.add_argument("--generate", action="store_true")
ap.add_argument("--lang")
ap.add_argument("--file", default="eval/questions.json")
a = ap.parse_args()

qs = json.load(open(a.file, encoding="utf-8"))
if a.lang:
    qs = [q for q in qs if q["lang"] == a.lang]

rows, ans_best, un_best = [], [], []
for q in qs:
    hits = retrieve(q["question"], None, k=TOP_K)
    best = min((h["dist"] for h in hits), default=9.9)
    near = [h for h in hits if h["dist"] <= MAX_DIST]
    r = {"id": q["id"], "lang": q["lang"], "question": q["question"], "best_dist": round(best, 3),
         "answerable": q["answerable"]}
    if q["answerable"]:
        text = " ".join(h["text"] for h in near).lower()
        r["kw_ok"] = any(k.lower() in text for k in q["expect_any"])
        r["src_ok"] = any(s in h["meta"]["page_url"] for h in near for s in q["expect_source"])
        r["ok"] = r["kw_ok"]
        ans_best.append(best)
    else:
        r["ok"] = len(near) == 0          # لازم ما يلاقي شي قريب كفاية
        un_best.append(best)
    if a.generate:
        text, _ = answer(q["question"])
        if q["answerable"]:
            r["answer_ok"] = any(k.lower() in text.lower() for k in q["expect_any"])
        else:
            r["answer_ok"] = text.strip() == NOT_FOUND.strip() or "ما لقيت" in text or "couldn't find" in text.lower()
        r["answer"] = text
    rows.append(r)
    flag = "PASS" if r["ok"] else "FAIL"
    extra = f" src={'y' if r.get('src_ok') else 'n'}" if q["answerable"] else ""
    print(f"{flag} {r['id']} [{q['lang']}] d={best:.3f}{extra}  {q['question'][:60]}")

A = [r for r in rows if r["answerable"]]
U = [r for r in rows if not r["answerable"]]
print("\n=== summary ===")
if A:
    print(f"retrieval keyword hit : {sum(r['ok'] for r in A)}/{len(A)}")
    print(f"expected source hit   : {sum(r['src_ok'] for r in A)}/{len(A)}")
    for lang in ("en", "ar"):
        s = [r for r in A if r["lang"] == lang]
        if s:
            print(f"  {lang}: {sum(r['ok'] for r in s)}/{len(s)}")
if U:
    print(f"unanswerable refused  : {sum(r['ok'] for r in U)}/{len(U)}")
if ans_best and un_best:
    hi, lo = max(ans_best), min(un_best)
    print(f"\nbest-dist answerable: median {statistics.median(ans_best):.3f}, max {hi:.3f}")
    print(f"best-dist unanswerable: min {lo:.3f}")
    if hi < lo:
        print(f"-> suggested MAX_DIST ≈ {(hi + lo) / 2:.2f}  (current {MAX_DIST})")
    else:
        print("-> the ranges overlap: no single MAX_DIST separates them; improve the KB or add a reranker")
if a.generate:
    g = [r for r in rows if "answer_ok" in r]
    print(f"\ngenerated answers ok : {sum(r['answer_ok'] for r in g)}/{len(g)}")
json.dump(rows, open("eval/results.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("details -> eval/results.json")
