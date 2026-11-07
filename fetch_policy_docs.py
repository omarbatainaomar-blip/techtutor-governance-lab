"""
تنزيل وثائق السياسات من مصادرها الرسمية حسب knowledge_base/policy_docs/manifest.yaml
  python fetch_policy_docs.py            # نزّل كل الوثائق التلقائية الناقصة
  python fetch_policy_docs.py --force    # أعد تنزيلها كلها
بعدين:  python -m governance.itu_ingest
الوثائق المكتوب عندها download: manual لازم تنزّلها من المتصفح وتحفظها بالمجلد بنفس الاسم (id.pdf).
"""
import argparse
import sys
import time
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parent
DIR = ROOT / "knowledge_base" / "policy_docs"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36 TechTutor-Governance-Sandbox/1.0 (ITU AI for Good hackathon; research use)")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def existing(d):
    base = DIR / d["file"]
    return [p for p in base.parent.glob(base.name + ".*")] if base.parent.exists() else []


def ext_for(resp, url):
    ct = resp.headers.get("content-type", "").lower()
    if "pdf" in ct or resp.content[:5] == b"%PDF-":
        return ".pdf"
    if "html" in ct:
        return ".html"
    if url.lower().endswith(".pdf"):
        return ".pdf"
    return ".html"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    docs = yaml.safe_load((DIR / "manifest.yaml").read_text(encoding="utf-8"))["documents"]
    ok, fail, manual = 0, [], []
    for d in docs:
        have = existing(d)
        if d.get("download") == "bundled":
            continue
        if d.get("download") == "manual":
            if not have:
                manual.append(d)
            continue
        if have and not a.force:
            print(f"  = {d['id']} (موجود)")
            continue
        try:
            r = requests.get(d["url"], headers={"User-Agent": UA, "Accept-Language": "en,ar;q=0.8"}, timeout=90)
            r.raise_for_status()
            if len(r.content) < 2000:
                raise ValueError(f"response too small ({len(r.content)} bytes)")
            ext = ext_for(r, d["url"])
            if d.get("format") == "pdf" and ext != ".pdf":
                # الموقع رجّع صفحة HTML (حماية Cloudflare، صفحة خطأ أو تسجيل دخول) بدل الـ PDF: ما بنحفظها كأنها الوثيقة
                raise ValueError("expected a PDF but the server returned HTML (download it manually from the browser)")
            if ext == ".html" and b"<html" not in r.content[:4000].lower() and b"<!doctype" not in r.content[:4000].lower():
                raise ValueError("unrecognised content type")
            target = (DIR / d["file"]).with_suffix(ext)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(r.content)
            ok += 1
            print(f"  ✓ {target.relative_to(DIR)}  ({len(r.content) // 1024} KB)")
        except Exception as e:
            fail.append((d, str(e)[:120]))
            print(f"  ✗ {d['id']}: {str(e)[:120]}")
        time.sleep(1.0)
    print(f"\nتم تنزيل {ok} | فشل {len(fail)} | يدوي ناقص {len(manual)}")
    for d, _ in fail:
        manual.append(d)
    if manual:
        print("\nنزّل هدول من المتصفح واحفظهم بالمكان المكتوب (PDF إذا متوفر، أو احفظ الصفحة HTML):")
        for d in manual:
            print(f"  - {DIR.name}/{d['file']}.pdf\n      {d['url']}")
    print("\nبعدها شغّل:  python -m governance.itu_ingest")


if __name__ == "__main__":
    main()
