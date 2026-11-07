"""
chat XVM: موقع الدردشة الكامل (تسجيل دخول + محادثات محفوظة + بث الأجوبة من نظام RAG).
  python server.py            ->  http://127.0.0.1:8000
مكتبات بايثون القياسية فقط للسيرفر نفسه. بيحتاج Ollama شغّال والفهرس مبني (build_index.py).
متغيرات اختيارية: HOST (الافتراضي 127.0.0.1) ، PORT (8000) ، COOKIE_SECURE=1 (عند استخدام HTTPS) ، OPEN_BROWSER=0
"""
import base64, hashlib, hmac, json, mimetypes, os, re, secrets, sqlite3, threading, time, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

import yaml

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
WEB = ROOT / "web"
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
DB_PATH = DATA / "chatxvm.sqlite"
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
COOKIE = "xvm_session"
IDLE_SECONDS = 30 * 60
MAX_SESSION_SECONDS = 12 * 3600          # حتى لو الكوكي بتتجدد، الجلسة بتنتهي بعد 12 ساعة
SECURE_COOKIE = os.getenv("COOKIE_SECURE") == "1"
OLLAMA = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MAX_BODY = 300_000
STATE_KEYS = {"chats", "tasks"}
MAX_STATE = 2_000_000
ALLOWED_HOSTS = {f"127.0.0.1:{PORT}", f"localhost:{PORT}"} | {h.strip().lower() for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h.strip()}
GOV_RUNNERS = {e.strip().lower() for e in os.getenv("GOV_RUNNERS", "").split(",") if e.strip()}   # فاضي = أي حساب مسجّل
MAX_LLM = threading.BoundedSemaphore(int(os.getenv("MAX_LLM", "2")))   # كم جواب بنفس الوقت (المعالج ما بيتحمّل أكثر)
MAX_STATE_BODY = MAX_STATE + 100_000      # PUT /api/state لازم يقبل لحد MAX_STATE وإلا الحفظ بيوقف بصمت

# ---------------------------------------------------------------- secret + database
_key_file = DATA / "secret.key"
if not _key_file.exists():
    _key_file.write_bytes(secrets.token_bytes(32))
    try:
        os.chmod(_key_file, 0o600)
    except OSError:
        pass
SECRET = _key_file.read_bytes()

_db = sqlite3.connect(DB_PATH, check_same_thread=False)
_db_lock = threading.Lock()
with _db_lock:
    _db.executescript("""
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, email TEXT UNIQUE NOT NULL,
                                     salt BLOB NOT NULL, hash BLOB NOT NULL, created INTEGER NOT NULL);
    CREATE TABLE IF NOT EXISTS state(user_id INTEGER NOT NULL, key TEXT NOT NULL, value TEXT NOT NULL,
                                     updated INTEGER NOT NULL, PRIMARY KEY(user_id, key));
    """)
    _db.commit()


def db(sql, args=(), one=False, write=False):
    with _db_lock:
        cur = _db.execute(sql, args)
        if write:
            _db.commit()
        return (cur.fetchone() if one else cur.fetchall())


# ---------------------------------------------------------------- passwords + sessions
def hash_pw(pw, salt):
    return hashlib.scrypt(pw.encode("utf-8"), salt=salt, n=2 ** 14, r=8, p=1, dklen=32)


_DUMMY_SALT = secrets.token_bytes(16)


_revoked = {}   # (uid, iat) -> وقت الانتهاء: جلسات انعمل لها تسجيل خروج


def make_token(kind, uid, iat=None):
    iat = int(iat or time.time())
    payload = f"{kind}|{uid}|{int(time.time()) + IDLE_SECONDS}|{secrets.token_hex(6)}|{iat}"
    body = base64.urlsafe_b64encode(payload.encode()).decode().rstrip("=")
    sig = hmac.new(SECRET, body.encode(), hashlib.sha256).hexdigest()
    return f"{body}.{sig}"


def read_token(tok):
    try:
        body, sig = tok.rsplit(".", 1)
        good = hmac.new(SECRET, body.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, good):
            return None
        kind, uid, exp, nonce, iat = base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)).decode().split("|")
        now = time.time()
        if int(exp) < now or int(iat) + MAX_SESSION_SECONDS < now or (int(uid), int(iat)) in _revoked:
            return None
        return {"kind": kind, "uid": int(uid), "nonce": nonce, "iat": int(iat)}
    except Exception:
        return None


# ---------------------------------------------------------------- throttling
_fail = {}       # key -> [count, locked_until]
_hits = {}       # session key -> [timestamps]
_active = set()  # sessions that currently stream an answer
_mem_lock = threading.Lock()
_gov_lock = threading.Lock()   # سيناريو حوكمة واحد بالمرة (النموذج المحلي ما بيتحمّل أكثر)


def locked_for(key):
    with _mem_lock:
        c = _fail.get(key)
        return max(0, int(c[1] - time.time())) if c and c[1] > time.time() else 0


def register_fail(key):
    with _mem_lock:
        c = _fail.setdefault(key, [0, 0, 0])
        c[0] += 1
        c[2] = time.time()
        if c[0] >= 5:
            c[0], c[1] = 0, time.time() + 60


def clear_fail(key):
    with _mem_lock:
        _fail.pop(key, None)


_last_prune = [0.0]


def _prune(now):
    """تنظيف دوري لقواميس الحماية عشان الذاكرة ما تضل تكبر."""
    if now - _last_prune[0] < 300:
        return
    _last_prune[0] = now
    for k in [k for k, v in _hits.items() if not v or now - v[-1] > 600]:
        _hits.pop(k, None)
    for k in [k for k, v in _fail.items() if v[1] < now and (v[0] == 0 or now - v[2] > 900)]:
        _fail.pop(k, None)
    for k in [k for k, exp in _revoked.items() if exp < now]:
        _revoked.pop(k, None)


def rate_ok(key, limit=20, window=60):
    now = time.time()
    with _mem_lock:
        _prune(now)
        arr = [t for t in _hits.get(key, []) if now - t < window]
        if len(arr) >= limit:
            _hits[key] = arr
            return False
        arr.append(now)
        _hits[key] = arr
        return True


# ---------------------------------------------------------------- app helpers
def load_topics():
    raw = yaml.safe_load(open(ROOT / "topics.yaml", encoding="utf-8"))
    return [{"id": k, "ar": v["ar"], "en": v["en"], "examples": v.get("examples", [])} for k, v in raw.items()]


TOPICS = load_topics()
TOPIC_IDS = {t["id"] for t in TOPICS} | {"all"}
EMAIL_RE = re.compile(r"^[^@\s]{1,64}@[^@\s]{1,189}\.[^@\s.]{1,63}$")   # خطي (بدون backtracking)


def rag_stream(*a, **k):
    import rag                      # استيراد متأخر: السيرفر بيشتغل حتى لو الفهرس لسا ما انبنى
    return rag.answer_stream(*a, **k)


def display_title(m):
    import rag                      # استيراد متأخر زي rag_stream
    return rag.display_title(m)


def format_sources(metas, text):
    prose = re.sub(r"```.*?(?:```|$)|`[^`\n]*`", " ", text, flags=re.S)     # أرقام داخل الكود مش استشهادات
    cited = {int(n) for n in re.findall(r"\[(\d{1,2})\]", prose)}
    chosen = [m for i, m in enumerate(metas, 1) if i in cited]
    related = False
    if not chosen and metas:
        chosen, related = metas[:2], True
    seen, out = set(), []
    for m in chosen:
        key = (m.get("page_url"), m.get("heading"))
        if key in seen:
            continue
        seen.add(key)
        out.append({"title": display_title(m), "heading": m.get("heading", ""),
                    "url": m.get("page_url", ""), "related": related})
    return out


def health():
    ollama = False
    try:
        import urllib.request
        urllib.request.urlopen(OLLAMA + "/api/tags", timeout=1.5).read(1)
        ollama = True
    except Exception:
        pass
    return {"ollama": ollama, "index": (ROOT / "knowledge_base" / "chroma").exists()}


CSP = ("default-src 'self'; script-src 'self'; style-src 'self' https://fonts.googleapis.com; "
       "font-src https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; "
       "base-uri 'none'; frame-ancestors 'none'; form-action 'self'")


# ---------------------------------------------------------------- HTTP handler
class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"
    timeout = 60                    # اتصال بطيء أو معلّق (slowloris) ما بيحجز thread للأبد
    server_version = "chatXVM"

    def log_message(self, fmt, *args):
        if os.getenv("XVM_LOG"):
            super().log_message(fmt, *args)

    # ---- low level
    def _sess(self):
        if not hasattr(self, "_s"):
            self._s = None
            for part in self.headers.get("Cookie", "").split(";"):
                k, _, v = part.strip().partition("=")
                if k == COOKIE:
                    self._s = read_token(v)
        return self._s

    def _headers(self, code, ctype, extra=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", CSP)
        self.send_header("Cache-Control", "no-store")
        s = getattr(self, "_s", None)
        if getattr(self, "_set_cookie", None) is not None:
            self._write_cookie(self._set_cookie)
        elif s:                                   # جلسة موجودة: نجدد مهلة الخمول
            self._write_cookie(make_token(s["kind"], s["uid"], s.get("iat")))
        for k, v in (extra or {}).items():
            self.send_header(k, v)

    def _write_cookie(self, tok, clear=False):
        attrs = f"{COOKIE}={tok}; Path=/; HttpOnly; SameSite=Lax; Max-Age={0 if clear else IDLE_SECONDS}"
        if SECURE_COOKIE:
            attrs += "; Secure"
        self.send_header("Set-Cookie", attrs)

    def _json(self, code, obj):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self._headers(code, "application/json; charset=utf-8", {"Content-Length": str(len(data))})
        self.end_headers()
        self.wfile.write(data)

    def _body(self, limit=MAX_BODY):
        n = int(self.headers.get("Content-Length") or 0)
        if n < 0 or n > limit:
            raise ValueError("too_large")
        raw = self.rfile.read(n) if n else b"{}"
        obj = json.loads(raw.decode("utf-8") or "{}")
        if not isinstance(obj, dict):
            raise ValueError("bad_json")
        return obj

    def _host_ok(self):
        return (self.headers.get("Host") or "").lower() in ALLOWED_HOSTS

    def _origin_ok(self):
        origin = self.headers.get("Origin")
        if self.headers.get("Sec-Fetch-Site") == "cross-site":
            return False
        return (not origin) or urlparse(origin).netloc.lower() in ALLOWED_HOSTS

    def _need_session(self):
        s = self._sess()
        if not s:
            self._json(401, {"error": "auth"})
        return s

    # ---- routing
    def do_GET(self):
        if not self._host_ok():                       # DNS rebinding: صفحة خبيثة باسم دومين ثاني
            return self._json(421, {"error": "host"})
        path = urlparse(self.path).path
        if path.startswith("/api/"):
            return self.api_get(path)
        return self.static(path)

    def do_POST(self):
        self._dispatch_write("POST")

    def do_PUT(self):
        self._dispatch_write("PUT")

    def _dispatch_write(self, method):
        path = urlparse(self.path).path
        if not self._host_ok():
            return self._json(421, {"error": "host"})
        if not self._origin_ok():
            return self._json(403, {"error": "origin"})
        if int(self.headers.get("Content-Length") or 0) > 0 and "application/json" not in (self.headers.get("Content-Type") or ""):
            return self._json(415, {"error": "json_only"})     # بيجبر المتصفح على preflight للطلبات من مواقع ثانية
        try:
            body = self._body(MAX_STATE_BODY if (method == "PUT" and path.startswith("/api/state/")) else MAX_BODY)
        except Exception as e:
            if str(e) == "too_large":
                return self._json(413, {"error": "too_large"})
            return self._json(400, {"error": "bad_json"})
        if method == "POST":
            return self.api_post(path, body)
        return self.api_put(path, body)

    # ---- static files
    def static(self, path):
        name = "index.html" if path in ("/", "") else path.lstrip("/")
        target = (WEB / name).resolve()
        if WEB.resolve() not in target.parents or not target.is_file():
            return self._json(404, {"error": "not_found"})
        data = target.read_bytes()
        ctype = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        if ctype.startswith("text/") or ctype in ("application/javascript", "image/svg+xml"):
            ctype += "; charset=utf-8"
        self._headers(200, ctype, {"Content-Length": str(len(data))})
        self.end_headers()
        self.wfile.write(data)

    # ---- API: GET
    def api_get(self, path):
        if path == "/api/health":
            return self._json(200, health())
        if path == "/api/topics":
            return self._json(200, {"topics": TOPICS})
        if path.startswith("/api/gov/"):
            return self.gov_get(path)
        s = self._need_session()
        if not s:
            return
        if path == "/api/me":
            if s["kind"] == "g":
                return self._json(200, {"guest": True})
            row = db("SELECT email FROM users WHERE id=?", (s["uid"],), one=True)
            if not row:
                return self._json(401, {"error": "auth"})
            return self._json(200, {"email": row[0]})
        m = re.fullmatch(r"/api/state/(\w+)", path)
        if m and m.group(1) in STATE_KEYS:
            if s["kind"] == "g":
                return self._json(200, {"value": None})
            row = db("SELECT value FROM state WHERE user_id=? AND key=?", (s["uid"], m.group(1)), one=True)
            return self._json(200, {"value": json.loads(row[0]) if row else None})
        return self._json(404, {"error": "not_found"})

    # ---- API: PUT
    def api_put(self, path, body):
        s = self._need_session()
        if not s:
            return
        m = re.fullmatch(r"/api/state/(\w+)", path)
        if not (m and m.group(1) in STATE_KEYS):
            return self._json(404, {"error": "not_found"})
        if s["kind"] == "g":
            return self._json(200, {"ok": True})              # الضيف ما بنحفظ له شي
        value = json.dumps(body.get("value"), ensure_ascii=False)
        if len(value) > MAX_STATE:
            return self._json(413, {"error": "too_large"})
        db("INSERT INTO state(user_id,key,value,updated) VALUES(?,?,?,?) "
           "ON CONFLICT(user_id,key) DO UPDATE SET value=excluded.value, updated=excluded.updated",
           (s["uid"], m.group(1), value, int(time.time())), write=True)
        return self._json(200, {"ok": True})

    # ---- API: POST
    def api_post(self, path, body):
        if path == "/api/register":
            return self.register(body)
        if path == "/api/login":
            return self.login(body)
        if path == "/api/guest":
            if not rate_ok("guestmk:" + self.client_address[0], limit=10, window=600):
                return self._json(429, {"error": "rate"})
            # رقم ثابت لكل ضيف (بيضل نفسه مع تجديد الكوكي) عشان حد الطلبات وقفل البث يشتغلوا عليه
            self._set_cookie = make_token("g", 1 + secrets.randbelow(2 ** 31 - 1))
            return self._json(200, {"guest": True})
        if path == "/api/logout":
            old = self._sess()
            if old:                                    # الكوكي القديمة ما بتعود تنفع حتى لو انسرقت
                with _mem_lock:
                    _revoked[(old["uid"], old["iat"])] = old["iat"] + MAX_SESSION_SECONDS
            self._s = None
            self._set_cookie = None
            self._headers(200, "application/json; charset=utf-8", {"Content-Length": "11"})
            self._write_cookie("", clear=True)
            self.end_headers()
            return self.wfile.write(b'{"ok":true}')
        if path == "/api/chat":
            return self.chat(body)
        if path == "/api/gov/run":
            return self.gov_run(body)
        return self._json(404, {"error": "not_found"})

    # ---- Governance Sandbox (multi-agent policy simulation)
    def gov_get(self, path):
        from governance import audit, config as GC, scenarios
        if path == "/api/gov/scenarios":
            return self._json(200, {"scenarios": scenarios.list_all()})
        if path.startswith("/api/gov/runs") and not self._need_session():
            return
        if path == "/api/gov/runs":
            return self._json(200, {"runs": audit.list_runs()})
        if path == "/api/gov/info":
            from governance import retrieval
            try:
                kb = retrieval.stats()
            except Exception:
                kb = {}
            return self._json(200, {"provider": GC.LLM_PROVIDER, "chat_model": GC.GEMINI_MODEL if GC.LLM_PROVIDER == "gemini" else GC.CHAT_MODEL,
                                    "embed_model": GC.EMBED_MODEL, "kb": kb, "running": _gov_lock.locked()})
        m = re.fullmatch(r"/api/gov/runs/([A-Za-z0-9_\-]{1,100})(\.jsonl|\.md)?", path)
        if m:
            p = GC.AUDIT_DIR / f"{m.group(1)}.jsonl"
            if not p.is_file():
                return self._json(404, {"error": "not_found"})
            recs = audit.read_log(p)
            if m.group(2) == ".jsonl":
                return self._download(p.read_bytes(), "application/x-ndjson; charset=utf-8", p.name)
            if m.group(2) == ".md":
                from governance import report
                return self._download(report.render(recs).encode("utf-8"), "text/markdown; charset=utf-8", p.stem + ".md")
            ok, bad = audit.verify_chain(recs)
            return self._json(200, {"run_id": m.group(1), "events": recs, "chain_ok": ok, "chain_broken_at": bad})
        return self._json(404, {"error": "not_found"})

    def _download(self, data, ctype, name):
        self._headers(200, ctype, {"Content-Length": str(len(data)), "Content-Disposition": f'attachment; filename="{name}"'})
        self.end_headers()
        self.wfile.write(data)

    def gov_run(self, body):
        """بيشغّل سيناريو وبيبث أحداث السجل مباشرة (NDJSON). سيناريو واحد بالمرة على السيرفر كله."""
        s = self._need_session()
        if not s:
            return
        if s["kind"] == "g":
            return self._json(403, {"error": "login_required"})
        if GOV_RUNNERS:
            row = db("SELECT email FROM users WHERE id=?", (s["uid"],), one=True)
            if not row or row[0].lower() not in GOV_RUNNERS:
                return self._json(403, {"error": "not_allowed"})
        from governance import scenarios
        from governance.coordinator import Coordinator
        from governance import config as GC
        sid = str(body.get("scenario", ""))
        if not re.fullmatch(r"[A-Za-z0-9_\-]{1,80}", sid):
            return self._json(400, {"error": "bad_scenario"})
        path = (GC.SCENARIO_DIR / f"{sid}.yaml").resolve()
        if path.parent != GC.SCENARIO_DIR.resolve() or not path.is_file():
            return self._json(404, {"error": "not_found"})
        try:
            sc = scenarios.load(path)
        except Exception:
            return self._json(404, {"error": "not_found"})
        lang = "ar" if body.get("lang") == "ar" else "en"
        if not _gov_lock.acquire(blocking=False):
            return self._json(409, {"error": "busy"})
        if not rate_ok(f"gov:{s['uid']}", limit=6, window=3600):      # بعد القفل: رفض "busy" ما بيستهلك الحصة
            _gov_lock.release()
            return self._json(429, {"error": "rate"})
        try:
            self._headers(200, "application/x-ndjson; charset=utf-8", {"X-Accel-Buffering": "no"})
            self.end_headers()
            gone = []

            def push(rec):
                if gone:
                    return
                try:
                    self._emit({"t": "event", "v": rec})
                except (BrokenPipeError, ConnectionResetError, OSError):
                    gone.append(1)          # المتصفح سكّر: السيناريو بيكمل وبينحفظ بالسجل
            try:
                co = Coordinator(sc, lang=lang, listener=push, owner=s["uid"],
                                 max_seconds=int(os.getenv("GOV_MAX_SECONDS", "7200")))
                run_id = co.run()
                if not gone:
                    self._emit({"t": "done", "v": run_id})
            except Exception as e:
                print(f"[gov error] {type(e).__name__}: {e}")
                if not gone:
                    try:
                        self._emit({"t": "error", "v": "internal_error"})
                    except Exception:
                        pass
        finally:
            _gov_lock.release()

    def register(self, body):
        email = str(body.get("email", ""))[:254].strip().lower()
        pw = str(body.get("password", ""))
        ip = self.client_address[0]
        wait = locked_for("ip:" + ip)
        if wait:
            return self._json(429, {"error": "locked", "retry": wait})
        if not rate_ok("reg:" + ip, limit=5, window=600):      # حد لإنشاء الحسابات من نفس IP
            return self._json(429, {"error": "rate"})
        if not EMAIL_RE.match(email) or len(email) > 254:
            return self._json(400, {"error": "bad_email"})
        if len(pw) < 8 or len(pw) > 200 or not re.search(r"[A-Za-z\u0600-\u06FF]", pw) or not re.search(r"\d", pw):
            return self._json(400, {"error": "weak_password"})
        salt = secrets.token_bytes(16)
        try:
            db("INSERT INTO users(email,salt,hash,created) VALUES(?,?,?,?)",
               (email, salt, hash_pw(pw, salt), int(time.time())), write=True)
        except sqlite3.IntegrityError:
            return self._json(409, {"error": "exists"})
        uid = db("SELECT id FROM users WHERE email=?", (email,), one=True)[0]
        self._set_cookie = make_token("u", uid)
        return self._json(200, {"email": email})

    def login(self, body):
        email = str(body.get("email", ""))[:254].strip().lower()
        pw = str(body.get("password", ""))
        keys = ["em:" + email, "ip:" + self.client_address[0]]
        wait = max(locked_for(k) for k in keys)
        if wait:
            return self._json(429, {"error": "locked", "retry": wait})
        row = db("SELECT id,salt,hash FROM users WHERE email=?", (email,), one=True)
        calc = hash_pw(pw[:200], row[1] if row else _DUMMY_SALT)           # نفس الزمن حتى لو البريد غير موجود
        if not row or not hmac.compare_digest(calc, row[2]):
            for k in keys:
                register_fail(k)
            return self._json(401, {"error": "bad_credentials"})
        for k in keys:
            clear_fail(k)
        self._set_cookie = make_token("u", row[0])
        return self._json(200, {"email": email})

    # ---- chat (بث NDJSON)
    def chat(self, body):
        s = self._need_session()
        if not s:
            return
        key = f"{s['kind']}:{s['uid']}"
        if s["kind"] == "g" and not rate_ok("gip:" + self.client_address[0], limit=60):
            return self._json(429, {"error": "rate"})          # سقف إضافي لكل IP للضيوف
        message = str(body.get("message", "")).strip()[:4000]
        if not message:
            return self._json(400, {"error": "empty"})
        topic = body.get("topic") if body.get("topic") in TOPIC_IDS else "all"
        history = []
        for h in (body.get("history") or [])[-8:]:
            if isinstance(h, dict) and h.get("role") in ("user", "assistant") and isinstance(h.get("content"), str):
                history.append({"role": h["role"], "content": h["content"][:4000]})
        att = body.get("attachment")
        attachment = None
        if isinstance(att, dict) and isinstance(att.get("text"), str) and att["text"].strip():
            attachment = {"name": str(att.get("name", "file"))[:80], "text": att["text"][:20000]}
        if not rate_ok(key):
            return self._json(429, {"error": "rate"})
        with _mem_lock:
            if key in _active:
                return self._json(409, {"error": "busy"})
            _active.add(key)
        if not MAX_LLM.acquire(blocking=False):            # عدد محدود من الأجوبة بنفس الوقت على السيرفر كله
            with _mem_lock:
                _active.discard(key)
            return self._json(503, {"error": "busy"})
        gen = None
        try:
            self._headers(200, "application/x-ndjson; charset=utf-8", {"X-Accel-Buffering": "no"})
            self.end_headers()
            last_text, last_src = "", []
            try:
                gen = rag_stream(message, history, topic, attachment)
                for text, srcs in gen:
                    last_text, last_src = text, srcs
                    self._emit({"t": "text", "v": text})
                self._emit({"t": "sources", "v": format_sources(last_src, last_text)})
                self._emit({"t": "done"})
            except (BrokenPipeError, ConnectionResetError):
                pass                                        # المستخدم ضغط إلغاء
            except Exception as e:
                print(f"[chat error] {type(e).__name__}: {e}")      # التفاصيل بالسجل بس، مش للمستخدم
                try:
                    self._emit({"t": "error", "v": "internal_error"})
                except Exception:
                    pass
        finally:
            if gen is not None:
                try:
                    gen.close()
                except Exception:
                    pass
            MAX_LLM.release()
            with _mem_lock:
                _active.discard(key)

    def _emit(self, obj):
        self.wfile.write((json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8"))
        self.wfile.flush()


def main():
    if HOST not in ("127.0.0.1", "localhost", "::1") and not SECURE_COOKIE:
        print("⚠️  السيرفر مفتوح على الشبكة بدون HTTPS: كلمات السر والكوكيز بتنتقل بدون تشفير. "
              "استخدم HTTPS (COOKIE_SECURE=1) أو خليه على 127.0.0.1")
    srv = ThreadingHTTPServer((HOST, PORT), Handler)
    srv.daemon_threads = True
    url = f"http://{'127.0.0.1' if HOST in ('0.0.0.0', '') else HOST}:{PORT}"
    print(f"chat XVM جاهز على {url}   (Ctrl+C للإيقاف)")
    if os.getenv("OPEN_BROWSER", "1") != "0":
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nتم الإيقاف")


if __name__ == "__main__":
    main()
