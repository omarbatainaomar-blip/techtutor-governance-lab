"""تشخيص Ollama:  python test_ollama.py"""
import os, requests

H = os.getenv("OLLAMA_HOST", "http://localhost:11434")
EMB = os.getenv("EMBED_MODEL", "bge-m3")
CHAT = os.getenv("CHAT_MODEL", "qwen2.5:7b")
OPT = {"num_gpu": int(os.environ["OLLAMA_NUM_GPU"])} if os.getenv("OLLAMA_NUM_GPU") not in (None, "") else {}
print("GPU option:", OPT or "default (Ollama decides)")


def step(name, fn):
    try:
        print(f"[ok]   {name}: {fn()}")
    except Exception as e:
        print(f"[FAIL] {name}: {e}")


def tags():
    r = requests.get(f"{H}/api/tags", timeout=10)
    return ", ".join(m["name"] for m in r.json()["models"])


def post(path, body):
    if OPT:
        body = {**body, "options": OPT}
    r = requests.post(f"{H}{path}", json=body, timeout=600)
    if r.status_code != 200:
        raise RuntimeError(f"{r.status_code} {r.text[:500]}")
    return r.json()


step("server + models", tags)
step(f"embed (short, {EMB})", lambda: f"dim={len(post('/api/embed', {'model': EMB, 'input': ['hello']})['embeddings'][0])}")
step("embed (Arabic)", lambda: f"dim={len(post('/api/embed', {'model': EMB, 'input': ['ما هو بروتوكول TCP؟']})['embeddings'][0])}")
step("embed (batch of 16 long)", lambda: f"n={len(post('/api/embed', {'model': EMB, 'input': ['network ' * 300] * 16, 'truncate': True})['embeddings'])}")
step(f"chat ({CHAT})", lambda: post("/api/chat", {"model": CHAT, "stream": False, "messages": [{"role": "user", "content": "Say hi in 3 words"}]})["message"]["content"])
