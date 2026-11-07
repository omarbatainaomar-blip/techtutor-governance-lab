"""سجل تدقيق (audit log) بصيغة JSONL، كل سطر مربوط بالسطر اللي قبله بـ SHA-256 (hash chain).
أي تعديل لاحق على السجل بيكسر السلسلة وبيبين بـ verify_chain(). هاد بيحقق شرط Auditability بالمسابقة.
"""
import hashlib
import json
import threading
import time
import uuid
from datetime import datetime, timezone

from . import config as C

GENESIS = "0" * 64


def _digest(prev, rec):
    body = json.dumps(rec, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256((prev + body).encode("utf-8")).hexdigest()


def new_run_id(prefix="run"):
    return f"{prefix}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:6]}"


class AuditLog:
    def __init__(self, run_id, directory=None, listener=None):
        self.run_id = run_id
        self.dir = directory or C.AUDIT_DIR
        self.dir.mkdir(parents=True, exist_ok=True)
        self.path = self.dir / f"{run_id}.jsonl"
        self.prev = GENESIS
        self.seq = 0
        self.listener = listener          # callback(rec) لبث الأحداث للواجهة مباشرة
        self._lock = threading.Lock()

    def log(self, type_, actor, payload):
        with self._lock:
            self.seq += 1
            rec = {"seq": self.seq, "run_id": self.run_id, "ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                   "type": type_, "actor": actor, "payload": payload, "prev_hash": self.prev}
            rec["hash"] = _digest(self.prev, rec)
            self.prev = rec["hash"]
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        if self.listener:
            try:
                self.listener(rec)
            except Exception:
                pass
        return rec

    def close(self):
        """بنسجّل آخر hash (رأس السلسلة) بملف فهرس منفصل: حذف أو إعادة كتابة السجل كامل بيبين بالمقارنة."""
        try:
            with open(self.dir / "index.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps({"run_id": self.run_id, "events": self.seq, "head_hash": self.prev,
                                    "closed_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}) + "\n")
        except OSError:
            pass


def read_log(path):
    """بيقرأ السجل سطر سطر؛ سطر تالف (مثلاً آخر سطر انقطع) ما بيضيّع التشغيل كله."""
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    out.append(json.loads(line))
                except ValueError:
                    out.append({"seq": None, "type": "corrupt_line", "payload": {}, "hash": None})
    return out


def head_hashes():
    idx = C.AUDIT_DIR / "index.jsonl"
    out = {}
    if idx.exists():
        for line in idx.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
                out[r["run_id"]] = r
            except (ValueError, KeyError):
                pass
    return out


def verify_chain(records, run_id=None):
    """بيرجع (True, None) إذا السلسلة سليمة وكاملة، أو (False, seq) لأول سطر معدّل/ناقص.
    كمان: الترقيم متصل من 1، أول حدث run_start، ونفس run_id، ورأس السلسلة بيطابق الفهرس إذا موجود."""
    prev = GENESIS
    rid = run_id or (records[0].get("run_id") if records else None)
    for i, rec in enumerate(records, 1):
        body = {k: v for k, v in rec.items() if k != "hash"}
        if (rec.get("seq") != i or rec.get("run_id") != rid or rec.get("prev_hash") != prev
                or _digest(prev, body) != rec.get("hash") or (i == 1 and rec.get("type") != "run_start")):
            return False, rec.get("seq") or i
        prev = rec["hash"]
    known = head_hashes().get(rid) if rid else None
    if known and (known.get("head_hash") != prev or known.get("events") != len(records)):
        return False, len(records)          # أحداث انحذفت من الآخر أو السجل انكتب من جديد
    return True, None


def is_complete(records):
    return bool(records) and records[-1].get("type") == "run_end"


def list_runs():
    out = []
    if not C.AUDIT_DIR.exists():
        return out
    for p in sorted(C.AUDIT_DIR.glob("*.jsonl"), reverse=True):
        if p.name == "index.jsonl":
            continue
        try:
            recs = read_log(p)
            if not recs:
                continue
            start = next((r for r in recs if r.get("type") == "run_start"), recs[0])
            end = next((r for r in reversed(recs) if r.get("type") == "run_end"), None)
            sp = start.get("payload") or {}
            out.append({"run_id": p.stem, "scenario": sp.get("scenario_id"), "title": sp.get("title"),
                        "started": start.get("ts"), "finished": bool(end),
                        "final": ((end or {}).get("payload") or {}).get("final_status") or ("INCOMPLETE" if not end else None),
                        "events": len(recs), "mtime": int(p.stat().st_mtime or time.time())})
        except Exception:
            out.append({"run_id": p.stem, "final": "CORRUPT", "events": 0, "finished": False})
    return out
