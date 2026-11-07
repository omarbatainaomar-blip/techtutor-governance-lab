"""الوكلاء + بروتوكول الرسائل بينهم.

كل وكيل إله: تفويض (mandate)، فئات بحث خاصة فيه (ما بيشوف كل قاعدة المعرفة)، ومعلومات وصلته هو بس
(information asymmetry: السيناريو بيوزّع المعلومات على دفعات ولجهات معيّنة). الوكيل بيرجع JSON ثابت،
وبعدين بوابة الأدلة بتتحقق من كل اقتباس قبل ما نعتمد قراره.

ملاحظة: الوكلاء بيحاكوا جهات رسمية لأغراض الاختبار فقط، وما بيمثّلوا مواقفها الرسمية.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from pathlib import Path

import yaml

from . import config as C
from . import evidence, llm, retrieval

VERDICTS = ("APPROVE", "CONDITIONS", "BLOCK", "NEED_INFO")
VERDICT_RANK = {"APPROVE": 0, "CONDITIONS": 1, "NEED_INFO": 2, "BLOCK": 3}
RISKS = ("low", "medium", "high")
ORDER = ["tutor", "policy_advisor", "data_office", "moe", "ai_office"]
INBOX_CHARS = 3000


@dataclass
class Message:
    """وحدة بروتوكول التواصل بين الوكلاء (inter-agent protocol)."""
    sender: str
    recipient: str
    kind: str            # QUESTION | ANSWER | NOTIFY
    content: str
    stage: int
    ref_seq: int | None = None   # رقم الحدث بالسجل اللي ولّد الرسالة

    def to_dict(self):
        return asdict(self)


def load_personas(path=None):
    path = path or Path(__file__).with_name("personas.yaml")
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


SYSTEM_TMPL = """{mandate}

This is a SIMULATION for testing AI governance; you simulate the role above and do not state official positions.
You are agent "{aid}" in a multi-agent governance sandbox. Other agents: {others}.
Protocol rules:
1. You only know your BRIEFING (information released to you) and MESSAGES addressed to you. Other agents may hold
   information you do not have. If something you need is missing, use verdict NEED_INFO and ask a specific agent.
   Claims from the regulated party (tutor/operator) are unverified until supported by evidence.
2. Ground every legal or policy statement in the numbered PASSAGES. For each one add a citation with the passage
   number and an EXACT quote copied word-for-word from that passage (8 to 40 words, do not drop words such as
   "not", "no", "without" or change numbers). Quotes are machine-checked; invented, shortened or paraphrased quotes
   are rejected. BLOCK, CONDITIONS and APPROVE all need at least one verified, relevant quote, otherwise they are
   automatically turned into NEED_INFO. Passages marked [free zone] or [international] do not bind UAE public
   schools; use them only as comparison. Passages marked [UAE guidance, non-binding] (strategies, charters, guides,
   principles) can support CONDITIONS but never BLOCK: BLOCK needs an unmarked binding UAE law or school policy.
   Do not repeat a question you already asked; wait for the answer.
3. If the passages do not cover the issue, say so in the assessment; never invent laws, articles, durations or numbers.
4. Use "messages" to answer questions or to notify another agent about an incident they must know.
5. Be brief and concrete. {lang_rule}
Return ONLY a JSON object with exactly these keys:
{{"assessment": "2-4 sentences", "verdict": "APPROVE|CONDITIONS|BLOCK|NEED_INFO", "risk": "low|medium|high",
 "conditions": ["concrete condition or mitigation"], "citations": [{{"ref": 1, "quote": "exact words from passage 1"}}],
 "questions": [{{"to": "agent_id", "question": "..."}}], "messages": [{{"to": "agent_id", "text": "answer or notification"}}],
 "rationale": ["short reasoning step", "..."]}}"""

LANG_RULE = {
    "en": "Write in English.",
    "ar": "Write assessment, conditions, questions, messages and rationale in Arabic; keep quotes in the passage's original language.",
}
SCOPE_TAG = {"free_zone": " [free zone]", "international": " [international]", "standard": " [standard]",
             "federal_guidance": " [UAE guidance, non-binding]", "emirate_guidance": " [UAE guidance, non-binding]"}
DUP_SIM = 0.6          # تشابه الكلمات اللي فوقه بنعتبر السؤال/الرسالة مكررة


def format_passages(hits, prefix="", max_chars=None):
    max_chars = max_chars or C.PASSAGE_CHARS
    lines = []
    for i, h in enumerate(hits, 1):
        m = h["meta"]
        where = []
        if m.get("page") not in (None, -1, ""):
            where.append(f"p.{m['page']}")
        if m.get("article"):
            where.append(f"Art. {m['article']}")
        loc = (", " + ", ".join(where)) if where else ""
        text = h["text"] if len(h["text"]) <= max_chars else h["text"][:max_chars] + " …"
        tag = SCOPE_TAG.get(m.get("binding_scope", ""), "")
        lines.append(f"[{prefix}{i}] ({m.get('title', '?')} — {m.get('issuer', '') or m.get('category', '')}{loc}){tag}\n{text}")
    return "\n\n".join(lines) if lines else "(no relevant passages found in the knowledge base)"


class Agent:
    def __init__(self, aid, persona, lang="en"):
        self.id = aid
        self.p = persona
        self.lang = lang
        self.briefing: list[dict] = []        # المعلومات اللي وصلت لهالوكيل بس
        self.inbox: list[Message] = []
        self.last: dict | None = None
        self.tainted: set = set()             # أرقام انعلّمت مخترعة (المنسّق بيشاركها بين كل الوكلاء)
        self.sent: list = []                  # (مرحلة، لمين، كلمات) لكل سؤال/رسالة بعتها، لكشف التكرار

    @property
    def authority(self):
        return bool(self.p.get("authority"))

    @property
    def role(self):
        return self.p.get("role")

    def receive(self, item):
        self.briefing.append(item)

    def needs_turn(self):
        """سؤال لأي وكيل، أو جواب/إشعار لجهة رسمية = لازم يرد بنفس المرحلة."""
        return any(m.kind == "QUESTION" or (self.authority and m.kind in ("ANSWER", "NOTIFY")) for m in self.inbox)

    has_questions = needs_turn                 # اسم قديم

    def retrieve(self, case, focus):
        new_info = " ".join(b["info"] for b in self.briefing[-2:])
        questions = " ".join(m.content for m in self.inbox if m.kind == "QUESTION")
        query = f"{focus} {new_info} {questions}".strip()[:1500] or case[:1500]
        hits = retrieval.search_policy(query, categories=self.p.get("categories"))
        if self.id in ("ai_office", "tutor"):
            fw = retrieval.search_framework(query, k=2)
            hits = retrieval.merge_hits(hits, fw, limit=C.POLICY_TOP_K + 2)
        return hits, query

    def _inbox_text(self):
        lines = []
        for m in self.inbox:
            tag = " [unverified claim from the regulated party]" if m.sender == "tutor" else ""
            lines.append(f"- {m.kind} from {m.sender}{tag}: {m.content}")
        text = "\n".join(lines)
        return (text[:INBOX_CHARS] + " …") if len(text) > INBOX_CHARS else (text or "- (none)")

    def _drop_repeats(self, out):
        """بيشيل سؤال/رسالة بتكرر شي بعته الوكيل لنفس الجهة بنفس المرحلة، أو رسالة بتكرر سؤال بنفس الرد.
        مرحلة جديدة = معلومات جديدة، فإعادة السؤال فيها مسموحة."""
        dropped, keep_q, keep_m = 0, [], []
        st = out.get("stage")
        seen = [(to, w) for s_, to, w in self.sent if s_ == st]
        for q in out["questions"]:
            w = _words(q["question"])
            if any(to == q["to"] and _jaccard(w, s) >= DUP_SIM for to, s in seen):
                dropped += 1
                continue
            keep_q.append(q)
            seen.append((q["to"], w))
        for a in out["messages"]:
            w = _words(a["text"])
            if any(to == a["to"] and _jaccard(w, s) >= DUP_SIM for to, s in seen):
                dropped += 1
                continue
            keep_m.append(a)
            seen.append((a["to"], w))
        out["questions"], out["messages"] = keep_q, keep_m
        self.sent = [(st, to, w) for to, w in seen]       # بنحتفظ بالمرحلة الحالية بس
        return dropped

    def respond(self, case, stage, focus, others):
        out = {"agent": self.id, "stage": stage}
        try:
            hits, query = self.retrieve(case, focus)
        except Exception as e:                                     # التضمين/Chroma تعطل: الوكيل بيكمل بدون مقاطع ويصعّد
            hits, query = [], ""
            out["retrieval_error"] = type(e).__name__
        brief = "\n".join(f"- (stage {b['stage']}) {b['info']}" for b in self.briefing[-4:]) or "- (nothing yet)"
        prev = (f"\nYOUR PREVIOUS VERDICT: {self.last['verdict']} — {self.last.get('assessment', '')[:300]}" if self.last else "")
        system = SYSTEM_TMPL.format(mandate=self.p["mandate"].strip(), aid=self.id, others=", ".join(others),
                                    lang_rule=LANG_RULE.get(self.lang, LANG_RULE["en"]))
        inbox_text = self._inbox_text()
        user = (f"CASE (shared with all agents):\n{case}\n\nCURRENT STAGE: {stage}\n\nYOUR BRIEFING:\n{brief}\n\n"
                f"MESSAGES TO YOU:\n{inbox_text}{prev}\n\nPASSAGES:\n{format_passages(hits)}")
        out["retrieval"] = {"query": query[:400], "hits": [{"ref": i, "chunk_id": h["id"], "doc_id": h["meta"].get("doc_id"),
                                                            "title": h["meta"].get("title"), "dist": h["dist"]}
                                                           for i, h in enumerate(hits, 1)]}
        try:
            data, meta = llm.chat_json([{"role": "system", "content": system}, {"role": "user", "content": user}])
            out["llm"] = meta
        except Exception as e:                                     # الوكيل نفسه ممكن يتعطل: سيناريو خطأ حقيقي
            out.update(assessment=f"Agent unavailable: {type(e).__name__}", verdict="NEED_INFO", risk="high",
                       conditions=[], citations_verified=[], citations_rejected=[], questions=[], messages=[],
                       rationale=[], flags=["agent_error"], error=type(e).__name__)
            self.last = out                                        # الرسائل بتضل بالـ inbox للمحاولة الجاية
            return out
        out.update(normalize_response(data, others))
        dropped = self._drop_repeats(out)
        if dropped:
            out["deduplicated"] = dropped
        verified, rejected = evidence.verify_citations(data.get("citations"), hits, visible_chars=C.PASSAGE_CHARS)
        issue = (focus + " " + " ".join(b["info"] for b in self.briefing[-2:])).strip()
        evidence.score_relevance(verified, issue)
        out["citations_verified"], out["citations_rejected"] = verified, rejected
        flags = []
        relevant = [c for c in verified if evidence.is_relevant(c, C.EVIDENCE_REL_MIN)]
        decisive = [c for c in verified if evidence.decisive(c, C.EVIDENCE_REL_MIN)]
        if any(c.get("relevance_error") for c in verified):
            flags.append("relevance_unchecked")
        if "retrieval_error" in out:
            flags.append("retrieval_error")

        def downgrade(flag):
            flags.append(flag)
            out["verdict_original"] = out["verdict"]
            out["verdict"] = "NEED_INFO"

        if self.authority:
            v = out["verdict"]
            if v in ("BLOCK", "CONDITIONS", "APPROVE") and not verified:
                downgrade("unsupported_approval" if v == "APPROVE" else "unsupported_verdict")
            elif v == "BLOCK" and not decisive:
                # إيقاف بده اقتباس طويل كفاية، ذو صلة، ومن نص إماراتي ملزم (مش منطقة حرة ولا مرجع دولي)
                downgrade("low_relevance_evidence" if not relevant else "non_binding_or_short_evidence")
            elif v in ("CONDITIONS", "APPROVE") and not relevant:
                downgrade("low_relevance_evidence")
        if verified and len(relevant) < len(verified):
            flags.append("low_relevance_citation")
        # أرقام بالتقييم أو الشروط (مدد، نسب، أعمار) لازم تكون موجودة بالمعلومات أو الاقتباسات أو الرسائل، وإلا ممكن تكون مخترعة
        trusted = " ".join([case, str(stage), " ".join(b["info"] for b in self.briefing),
                            " ".join((c.get("source_span") or c["quote"]) for c in verified),
                            " ".join(f"{h['meta'].get('title', '')} {h['meta'].get('article', '')} {h['meta'].get('year', '')}"
                                     for h in hits)])
        # رقم انعلّم مخترع عند أي وكيل ما بيصير موثّق لأنه وصل برسالة (إلا إذا موجود بمصدر موثوق)
        trusted_nums = set(_nums(trusted))
        laundered = {n for n in self.tainted if n not in trusted_nums}
        checked = " ".join([out["assessment"], " ".join(out["conditions"]),
                            " ".join(q["question"] for q in out["questions"]), " ".join(a["text"] for a in out["messages"])])
        unverified = unverified_numbers(checked, trusted + " " + inbox_text, exclude=laundered)
        if unverified:
            flags.append("unverified_numbers")
            out["unverified_numbers"] = unverified
            self.tainted.update(unverified)
        if rejected:
            flags.append("rejected_citations")
        if not hits:
            flags.append("no_passages")
        out["flags"] = flags
        self.inbox.clear()
        self.last = out
        return out


_NUM = re.compile(r"\d+(?:[.,]\d+)?")
_AR_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def _nums(text):
    t = str(text).translate(_AR_DIGITS)
    t = re.sub(r"(?<=\d),(?=\d{3}\b)", "", t)                 # 2,000 = 2000
    t = re.sub(r"(?m)^\s*\d{1,2}[.)]\s", " ", t)               # أرقام القوائم (1. 2) ...)
    return _NUM.findall(t)


def _words(text):
    return set(re.findall(r"\w{3,}", str(text).lower()))


def _jaccard(a, b):
    return len(a & b) / len(a | b) if a and b else 0.0


_UNITS = {"day": r"days?|يوم|يوما|يوماً|أيام|ايام", "week": r"weeks?|أسبوع|اسبوع|أسابيع|اسابيع",
          "month": r"months?|شهر|شهور|أشهر|اشهر", "year": r"years?|سنة|سنوات|عام|أعوام",
          "hour": r"hours?|ساعة|ساعات", "percent": r"%|٪|percent|بالمئة|بالمائة"}
_QTY = re.compile(r"(\d+(?:\.\d+)?)\s*(" + "|".join(f"(?P<{k}>{v})" for k, v in _UNITS.items()) + r")(?![A-Za-z])", re.I)


def _quantities(text):
    """{(رقم، وحدة)}: مدد ونسب زي "6 months" أو "١٢ شهراً" أو "81%"."""
    t = str(text).translate(_AR_DIGITS)
    return {(m.group(1), next(k for k in _UNITS if m.group(k))) for m in _QTY.finditer(t)}


def unverified_numbers(text, known, exclude=()):
    """الأرقام اللي بالنص ومش موجودة بالمصادر المعروفة (المعلومات، الرسائل، الاقتباسات، بيانات المقاطع).
    المدد والنسب لازم تطابق بالرقم والوحدة مع بعض (6 أشهر ما بتتوثّق لأنه في "المادة 6").
    exclude: أرقام انعلّمت مخترعة قبل، فما بتنحسب موثّقة حتى لو وصلت برسالة."""
    known_nums = set(_nums(known)) - set(exclude)
    known_qty = {q for q in _quantities(known) if q[0] not in set(exclude)}
    found = []
    for n in _nums(text):
        if n not in known_nums and n not in found:
            found.append(n)
    for n, unit in sorted(_quantities(text)):
        if (n, unit) not in known_qty and n not in found:
            found.append(n)
    return found[:6]


def _as_list(x):
    if x is None:
        return []
    return x if isinstance(x, list) else [x]


def normalize_response(d, others):
    """النماذج الصغيرة بتغلط بالأشكال: بنثبّت المفاتيح والقيم المسموحة."""
    if not isinstance(d, dict):
        d = {}
    verdict = str(d.get("verdict", "NEED_INFO")).upper().strip()
    verdict = {"APPROVED": "APPROVE", "APPROVE_WITH_CONDITIONS": "CONDITIONS", "CONDITIONAL": "CONDITIONS",
               "SUSPEND": "BLOCK", "REJECT": "BLOCK", "BLOCKED": "BLOCK"}.get(verdict, verdict)
    if verdict not in VERDICTS:
        verdict = "NEED_INFO"
    risk = str(d.get("risk", "medium")).lower().strip()
    qs = []
    for q in _as_list(d.get("questions")):
        if isinstance(q, dict) and q.get("question"):
            to = str(q.get("to", "")).strip()
            if to in others:
                qs.append({"to": to, "question": str(q["question"])[:500]})
    msgs = []
    for a in _as_list(d.get("messages")) + _as_list(d.get("answers")):     # answers = الصيغة القديمة
        if isinstance(a, dict) and (a.get("text") or a.get("answer")):
            to = str(a.get("to", "")).strip()
            if to in others:
                msgs.append({"to": to, "text": str(a.get("text") or a.get("answer"))[:600]})
    return {"assessment": str(d.get("assessment", ""))[:1200], "verdict": verdict,
            "risk": risk if risk in RISKS else "medium",
            "conditions": [str(c)[:300] for c in _as_list(d.get("conditions")) if str(c).strip()][:6],
            "questions": qs[:C.MAX_QUESTIONS], "messages": msgs[:3],
            "rationale": [str(r)[:300] for r in _as_list(d.get("rationale")) if str(r).strip()][:6]}
