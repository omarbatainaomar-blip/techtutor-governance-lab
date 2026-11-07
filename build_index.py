"""
يقرأ knowledge_chunks من الـ sqlite ويعمل embeddings عبر Ollama ويخزنها في Chroma.
  ollama pull bge-m3          # نموذج embeddings يدعم العربي والإنجليزي (وبيربط بينهم)
  python build_index.py
"""
import os, sqlite3, requests, chromadb, yaml

DB = os.getenv("KB_DB", "knowledge_base/education_technology_knowledge_base.sqlite")
CHROMA = "knowledge_base/chroma"
OLLAMA = os.getenv("OLLAMA_HOST", "http://localhost:11434")
EMBED_MODEL = os.getenv("EMBED_MODEL", "bge-m3")
# OLLAMA_NUM_GPU=0  ->  تشغيل على المعالج (CPU) إذا كرت الشاشة عم يعمل أخطاء CUDA
OPTS = {"num_gpu": int(os.environ["OLLAMA_NUM_GPU"])} if os.getenv("OLLAMA_NUM_GPU") not in (None, "") else None


def _post(texts):
    r = requests.post(f"{OLLAMA}/api/embed",
                      json={"model": EMBED_MODEL, "input": texts, "truncate": True, "keep_alive": "10m", **({"options": OPTS} if OPTS else {})},
                      timeout=900)
    if r.status_code != 200:
        raise RuntimeError(f"Ollama {r.status_code}: {r.text[:600]}")
    return r.json()["embeddings"]


def embed(texts):
    """دفعة واحدة أول شي؛ إذا فشلت منجرب كل نص لحاله لنعرف أي قطعة بتعمل المشكلة."""
    try:
        return _post(texts)
    except RuntimeError as e:
        print(f"\nبطّلت الدفعة تشتغل ({e}). بجرب القطع وحدة وحدة...")
        out = []
        for t in texts:
            try:
                out.append(_post([t])[0])
            except RuntimeError as e2:
                raise SystemExit(f"\nفشلت قطعة طولها {len(t)} حرف:\n{t[:150]!r}\n{e2}\n"
                                 "شغّل python test_ollama.py لتشخيص Ollama.")
        return out


def main():
    con = sqlite3.connect(DB)
    rows = con.execute(
        "select c.chunk_id, c.source_id, s.title, c.heading, c.content, c.language, c.page_url, c.topics "
        "from knowledge_chunks c join sources s using(source_id) order by c.chunk_id").fetchall()
    if not rows:
        raise SystemExit("knowledge_chunks فاضي. شغّل python ingest.py أول.")
    topics = list(yaml.safe_load(open("topics.yaml", encoding="utf-8")).keys())
    client = chromadb.PersistentClient(CHROMA)
    try:
        client.delete_collection("tech")
    except Exception:
        pass
    try:    # chromadb 1.x
        col = client.create_collection("tech", configuration={"hnsw": {"space": "cosine"}})
    except Exception:   # نسخ أقدم
        col = client.create_collection("tech", metadata={"hnsw:space": "cosine"})
    B = 16
    for i in range(0, len(rows), B):
        batch = rows[i:i + B]
        texts = [f"{r[2]} — {r[3]}\n{r[4]}" for r in batch]
        metas = []
        for r in batch:
            m = {"source_id": r[1], "source_title": r[2], "heading": r[3] or "", "lang": r[5] or "en",
                 "page_url": r[6] or "", "topics": r[7] or ""}
            for t in (r[7] or "").split(","):
                if t:
                    m[f"t_{t}"] = True
            metas.append(m)
        col.add(ids=[str(r[0]) for r in batch], documents=[r[4] for r in batch],
                embeddings=embed(texts), metadatas=metas)
        print(f"{min(i + B, len(rows))}/{len(rows)}", end="\r")
    print(f"\nindexed {len(rows)} chunks with {EMBED_MODEL}")


if __name__ == "__main__":
    main()
