"""
تشغيل سيناريو حوكمة من سطر الأوامر.
  python run_scenario.py --list
  python run_scenario.py s1_student_data_offshore            # بالإنجليزي (أدق مع النماذج الصغيرة)
  python run_scenario.py s1_student_data_offshore --lang ar  # مخرجات الوكلاء بالعربي
  python run_scenario.py --verify data/audit/<run>.jsonl     # التحقق من سلامة السجل
  python run_scenario.py --report data/audit/<run>.jsonl     # توليد تقرير Markdown من سجل قديم
النتيجة: data/audit/<run_id>.jsonl (سجل متسلسل) + reports/<run_id>.md
"""
import argparse
import os
import sys
from pathlib import Path

os.chdir(Path(__file__).resolve().parent)
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from governance import config as C, report, scenarios                      # noqa: E402
from governance.audit import read_log, verify_chain                         # noqa: E402
from governance.coordinator import Coordinator                              # noqa: E402

ICON = {"release": "📨", "agent_response": "🤖", "message": "✉️", "decision": "⚖️", "gap_analysis": "🧭",
        "run_start": "▶", "run_end": "■"}


def live(rec):
    p = rec["payload"]
    t = rec["type"]
    if t == "release":
        print(f"\n{ICON[t]} Stage {p['stage']} — {p.get('title_en')} → {', '.join(p['to'])}")
    elif t == "agent_response":
        lat = (p.get("llm") or {}).get("latency_s")
        print(f"  {ICON[t]} {rec['actor']:<15} {p.get('verdict'):<11} risk={p.get('risk'):<6} "
              f"✓{len(p.get('citations_verified', []))} ✗{len(p.get('citations_rejected', []))} "
              f"{'⚑' + ','.join(p['flags']) if p.get('flags') else ''} {f'({lat}s)' if lat else ''}")
    elif t == "message":
        print(f"     {ICON[t]} {p['sender']} → {p['recipient']}: {p['content'][:110]}")
    elif t == "decision":
        print(f"  {ICON[t]} DECISION: {p['status']} ({p['rule']})")
    elif t == "run_error":
        print(f"\n⚠️ RUN ERROR: {p.get('error')}")
    elif t == "run_end":
        for e in p.get("expectations") or []:
            print(f"   {'✅' if e.get('pass') else '❌'} expected: {e.get('check')} (actual: {e.get('actual')})")
    elif t == "gap_analysis":
        print(f"\n{ICON[t]} Gaps found: {len(p.get('gaps', []))}")
        for g in p.get("gaps", []):
            print(f"   - [{g.get('uae_status')}/{g.get('evidence_level')}] {g.get('title')}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scenario", nargs="?")
    ap.add_argument("--lang", default="en", choices=["en", "ar"])
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--verify")
    ap.add_argument("--report")
    a = ap.parse_args()
    if a.list:
        for s in scenarios.list_all():
            print(f"{s['id']:<32} {s.get('title_en', '')}  ({len(s.get('stages', []))} stages)")
        return
    if a.verify:
        ok, bad = verify_chain(read_log(a.verify))
        print("✅ audit chain intact" if ok else f"❌ chain broken at event {bad}")
        sys.exit(0 if ok else 1)
    if a.report:
        recs = read_log(a.report)
        out = C.REPORT_DIR / (Path(a.report).stem + ".md")
        C.REPORT_DIR.mkdir(exist_ok=True)
        out.write_text(report.render(recs), encoding="utf-8")
        print(out)
        return
    if not a.scenario:
        ap.error("scenario id or path required (see --list)")
    sc = scenarios.load(a.scenario)
    print(f"▶ {sc.get('title_en')}  | LLM: {C.LLM_PROVIDER} | embed: {C.EMBED_MODEL}")
    co = Coordinator(sc, lang=a.lang, listener=live)
    run_id = co.run()
    recs = read_log(co.log.path)
    C.REPORT_DIR.mkdir(exist_ok=True)
    out = C.REPORT_DIR / f"{run_id}.md"
    out.write_text(report.render(recs), encoding="utf-8")
    print(f"\n■ final: {co.status}\n  audit: {co.log.path}\n  report: {out}")


if __name__ == "__main__":
    main()
