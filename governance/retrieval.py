"""Embeddings عبر Ollama + البحث في مجموعات السياسات والإطار (Chroma)."""
import requests

from . import config as C

_client = None
_cols = {}


def client():
    global _client
    if _client is None:
        import chromadb
        try:
            from chromadb.config import Settings
            _client = chromadb.PersistentClient(str(C.CHROMA_DIR), settings=Settings(anonymized_telemetry=False))
        except Exception:
            _client = chromadb.PersistentClient(str(C.CHROMA_DIR))
    return _client


def collection(name, create=False):
    if name not in _cols:
        c = client()
        if create:
            try:    # chromadb 1.x
                _cols[name] = c.get_or_create_collection(name, configuration={"hnsw": {"space": "cosine"}})
            except Exception:
                _cols[name] = c.get_or_create_collection(name, metadata={"hnsw:space": "cosine"})
        else:
            _cols[name] = c.get_collection(name)
    return _cols[name]


def reset_collection(name):
    try:
        client().delete_collection(name)
    except Exception:
        pass
    _cols.pop(name, None)
    return collection(name, create=True)


def embed_many(texts, batch=16):
    out = []
    for i in range(0, len(texts), batch):
        part = texts[i:i + batch]
        r = requests.post(f"{C.OLLAMA}/api/embed", timeout=900, json={
            "model": C.EMBED_MODEL, "input": part, "truncate": True, "keep_alive": "10m",
            **({"options": C.GPU_OPT} if C.GPU_OPT else {})})
        if r.status_code != 200:
            raise RuntimeError(f"Ollama embed {r.status_code}: {r.text[:300]}")
        out.extend(r.json()["embeddings"])
    return out


def _search(col_name, query, k, where=None, max_dist=None):
    try:
        col = collection(col_name)
    except Exception:
        return []
    kw = {"query_embeddings": [embed_many([query])[0]], "n_results": k}
    if where:
        kw["where"] = where
    try:
        r = col.query(**kw)
    except Exception:
        _cols.pop(col_name, None)        # إعادة بناء المجموعة والسيرفر شغال
        r = collection(col_name).query(**kw)
    hits = [{"id": i, "text": d, "meta": m, "dist": round(x, 4)}
            for i, d, m, x in zip(r["ids"][0], r["documents"][0], r["metadatas"][0], r["distances"][0])]
    if max_dist is not None:
        hits = [h for h in hits if h["dist"] <= max_dist]
    return hits


def search_policy(query, categories=None, k=None, max_dist=None):
    where = None
    if categories:
        where = {"category": categories[0]} if len(categories) == 1 else {"category": {"$in": list(categories)}}
    return _search(C.POLICY_COLLECTION, query, k or C.POLICY_TOP_K, where,
                   C.POLICY_MAX_DIST if max_dist is None else max_dist)


def search_framework(query, k=3):
    return _search(C.FRAMEWORK_COLLECTION, query, k)


def merge_hits(*lists, limit=8):
    """دمج نتائج أكثر من بحث بدون تكرار، الأقرب أول."""
    seen, out = set(), []
    for h in sorted((h for l in lists for h in l), key=lambda h: h["dist"]):
        if h["id"] in seen:
            continue
        seen.add(h["id"])
        out.append(h)
    return out[:limit]


def stats():
    out = {}
    for name in (C.POLICY_COLLECTION, C.FRAMEWORK_COLLECTION):
        try:
            out[name] = collection(name).count()
        except Exception:
            out[name] = 0
    return out
