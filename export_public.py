"""ينسخ قاعدة البيانات لملف public.sqlite فيه فقط المصادر اللي عليها publish: true بـ sources.yaml
  python export_public.py   ->  knowledge_base/public.sqlite  (هاد اللي بتنشره على GitHub)
"""
import shutil, sqlite3, yaml

SRC = "knowledge_base/education_technology_knowledge_base.sqlite"
OUT = "knowledge_base/public.sqlite"
cfg = yaml.safe_load(open("sources.yaml", encoding="utf-8"))
ok = [s for s, c in cfg.items() if c.get("publish") is True]
shutil.copy(SRC, OUT)
con = sqlite3.connect(OUT)
con.execute(f"delete from knowledge_chunks where source_id not in ({','.join('?' * len(ok))})", ok)
con.commit()
con.execute("vacuum")
print("published sources:", ok, "| chunks:", con.execute("select count(*) from knowledge_chunks").fetchone()[0])
