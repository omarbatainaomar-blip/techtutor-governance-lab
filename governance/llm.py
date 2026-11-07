"""واجهة موحدة لنموذج التوليد: Ollama (افتراضي، محلي) أو Gemini (اختياري عبر LLM_PROVIDER=gemini).

كل وكيل بيستدعي chat_json() وبياخد dict. الدالة بترجع كمان معلومات (المزوّد، النموذج، الزمن) للسجل.
"""
import json
import re
import time

import requests

from . import config as C


class LLMError(RuntimeError):
    pass


def _ollama(messages, json_mode, temperature, max_tokens):
    r = requests.post(f"{C.OLLAMA}/api/chat", timeout=900, json={
        "model": C.CHAT_MODEL, "messages": messages, "stream": False,
        **({"format": "json"} if json_mode else {}),
        "options": {"temperature": temperature, "num_ctx": 8192, "num_predict": max_tokens, **C.GPU_OPT}})
    if r.status_code != 200:
        raise LLMError(f"ollama {r.status_code}: {r.text[:300]}")
    j = r.json()
    # done_reason=length يعني الرد انقطع (JSON ناقص)؛ وعدد التوكنات بيبين إذا قربنا من سياق النموذج
    return j["message"]["content"], {"provider": "ollama", "model": C.CHAT_MODEL, "done_reason": j.get("done_reason"),
                                     "prompt_tokens": j.get("prompt_eval_count"), "output_tokens": j.get("eval_count")}


def _gemini(messages, json_mode, temperature, max_tokens):
    if not C.GEMINI_API_KEY:
        raise LLMError("GEMINI_API_KEY is not set")
    system = "\n\n".join(m["content"] for m in messages if m["role"] == "system")
    contents = [{"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]}
                for m in messages if m["role"] != "system"]
    body = {"contents": contents,
            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens,
                                 **({"responseMimeType": "application/json"} if json_mode else {})}}
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{C.GEMINI_MODEL}:generateContent"
    # 429 (حد الطلبات) و 500/503 (ضغط مؤقت على سيرفرات Google): بنعيد المحاولة مع انتظار متزايد
    for attempt, wait in enumerate((0, 5, 15, 30, 60)):
        if wait:
            print(f"   … gemini {r.status_code}, retry in {wait}s ({attempt}/4)", flush=True)
            time.sleep(wait)
        r = requests.post(url, json=body, timeout=120, headers={"x-goog-api-key": C.GEMINI_API_KEY})
        if r.status_code not in (429, 500, 503):
            break
    if r.status_code != 200:
        raise LLMError(f"gemini {r.status_code}: {r.text[:300]}")
    data = r.json()
    try:
        text = "".join(p.get("text", "") for p in data["candidates"][0]["content"]["parts"])
    except (KeyError, IndexError):
        raise LLMError(f"gemini: empty response {str(data)[:300]}")
    return text, {"provider": "gemini", "model": C.GEMINI_MODEL}


_gemini_off_until = [0.0]   # قاطع دائرة: بعد فشل Gemini بنوقف نحاول فترة بدل ما نضيّع دقيقتين كل رد


def chat(messages, *, json_mode=False, temperature=0.1, max_tokens=None):
    """بيرجع (النص، meta). meta فيها provider/model/latency_s/fallback."""
    max_tokens = max_tokens or C.AGENT_MAX_TOKENS
    t0 = time.time()
    if C.LLM_PROVIDER == "gemini" and time.time() < _gemini_off_until[0] and C.LLM_FALLBACK:
        text, meta = _ollama(messages, json_mode, temperature, max_tokens)
        meta["fallback_from"] = "gemini: paused after earlier failure"
    elif C.LLM_PROVIDER == "gemini":
        try:
            text, meta = _gemini(messages, json_mode, temperature, max_tokens)
        except Exception as e:
            if not C.LLM_FALLBACK:
                raise
            msg = str(e)
            # الحصة خلصت => طول التشغيل؛ ضغط/انقطاع => 10 دقائق
            _gemini_off_until[0] = time.time() + (6 * 3600 if ("quota" in msg.lower() or "429" in msg) else 600)
            print(f"   ⚠ Gemini unavailable ({msg[:60]}…) → using local Ollama", flush=True)
            text, meta = _ollama(messages, json_mode, temperature, max_tokens)
            meta["fallback_from"] = f"gemini: {msg[:120]}"
    else:
        text, meta = _ollama(messages, json_mode, temperature, max_tokens)
    meta["latency_s"] = round(time.time() - t0, 2)
    return text, meta


def parse_json(text):
    """النماذج الصغيرة أحياناً بتحط JSON داخل ``` أو بتزيد كلام قبله؛ بناخد أول كائن صالح."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
        if isinstance(obj, list) and obj and isinstance(obj[0], dict):   # بعض النماذج بترجع [ {...} ]
            return obj[0]
    except Exception:
        pass
    start = text.find("{")
    while start != -1:
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        obj = json.loads(text[start:i + 1])
                        if isinstance(obj, dict):
                            return obj
                    except Exception:
                        pass
                    break
        start = text.find("{", start + 1)
    raise LLMError("no valid JSON in model output")


def chat_json(messages, **kw):
    """chat() + JSON. إذا الرد انقطع (طول) بنعيد بضعف الحد؛ إذا JSON غلط بنعيد مرة وحدة مع تذكير صريح."""
    text, meta = chat(messages, json_mode=True, **kw)
    try:
        return parse_json(text), meta
    except LLMError:
        pass
    if meta.get("done_reason") == "length":
        kw2 = dict(kw, max_tokens=2 * (kw.get("max_tokens") or C.AGENT_MAX_TOKENS))
        text, meta2 = chat(messages, json_mode=True, **kw2)
        meta2["retried"] = "length"
    else:
        retry = messages + [{"role": "assistant", "content": text[:2000]},
                            {"role": "user", "content": "Your previous output was not valid JSON. Return ONLY the JSON object, nothing else."}]
        text, meta2 = chat(retry, json_mode=True, **kw)
        meta2["retried"] = "invalid_json"
    return parse_json(text), meta2
