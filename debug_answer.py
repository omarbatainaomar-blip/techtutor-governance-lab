"""تشخيص: بيشغّل سؤال عبر المدرّس وبيطبع كل مرحلة (المقاطع، الجواب الخام، التنظيف، الترجمة، فحص المصادر).
python debug_answer.py "What is subnetting?" networking --after "شو الفرق بين TCP و UDP؟"
"""
import argparse
import rag

ap = argparse.ArgumentParser()
ap.add_argument("question")
ap.add_argument("topic", nargs="?", default=None)
ap.add_argument("--after", default="", help="سؤال سابق بالمحادثة (اختياري)")
ap.add_argument("--file", default="", help="ملف نصي مرفق (اختياري)")
a = ap.parse_args()
att = None
if a.file:
    from pathlib import Path as _P
    att = {"name": _P(a.file).name, "text": _P(a.file).read_text(encoding="utf-8")}
history = []
if a.after:
    prev = ""
    for prev, _ in rag.answer_stream(a.after, [], a.topic):
        pass
    history = [{"role": "user", "content": a.after}, {"role": "assistant", "content": prev}]
    print("== previous answer ok:", prev[:80].replace("\n", " "), "\n")

print("== language:", rag.detect_language(a.question), "| queries:", rag.search_queries(a.question, rag.clean_history(history)))
for h in rag.retrieve_merged(a.question, rag.clean_history(history), a.topic):
    print(f"   {h['dist']:.3f}  {h['meta'].get('heading')}")


def wrap(name):
    f = getattr(rag, name)
    def g(*args, **kw):
        out = f(*args, **kw)
        print(f"\n== {name} -> {str(out)[:600]}")
        return out
    setattr(rag, name, g)


for n in ("fix_language", "ensure_language", "grounded"):
    wrap(n)
_attr = rag.attribute
def attribute(text, hits, attachment=None, embed_fn=None):
    ratio, res = _attr(text, hits, attachment, embed_fn)
    print(f"\n== attribute: supported ratio {ratio:.2f} (need {rag.SUPPORT_MIN}, sentence sim >= {rag.SUPPORT_SIM})")
    for s, label, sim in res:
        print(f"   {sim:.3f} {'['+label+']' if label else '   '}  {s[:110]}")
    return ratio, res
rag.attribute = attribute
final = None
print("== attachment:", att["name"] if att else None)
for final, src in rag.answer_stream(a.question, history, a.topic, att):
    pass
print("\n== cites:", rag._cites(final))
print("== FINAL:\n", final)
