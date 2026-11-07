"""المنسّق (Coordinator / MLFO): بيوزّع المعلومات على مراحل، بيدير جولات الرسائل بين الوكلاء،
وبياخد القرار النهائي بقواعد حتمية مكتوبة (مش بالنموذج اللغوي) — النموذج بيقترح والقواعد بتقرر.
كل خطوة بتنكتب بسجل التدقيق المتسلسل (audit.py).
"""
from __future__ import annotations

import hashlib
import json
import re
import time

from . import config as C
from . import evidence, llm, retrieval
from .agents import Agent, Message, ORDER, VERDICT_RANK, format_passages, load_personas, unverified_numbers
from .audit import AuditLog, new_run_id

Y3172_NODES = ["SRC", "C", "PP", "M", "P", "D", "SINK", "MLFO", "Sandbox"]


def _node(x):
    """النموذج أحياناً بينسخ القائمة كلها (SRC|C|PP...) أو بيكتب "P (Policy)": بناخد عقدة وحدة صالحة أو فاضي."""
    x = re.sub(r"\(.*?\)", "", str(x or ""))
    parts = [p.strip() for p in x.replace("/", "|").replace(",", "|").split("|") if p.strip()]
    if len(parts) != 1:
        return ""
    return next((n for n in Y3172_NODES if n.lower() == parts[0].lower()), "")


def _dimension_names():
    try:
        return [d["name"] for d in json.loads(C.FRAMEWORK_JSON.read_text(encoding="utf-8"))["dimensions"]]
    except Exception:
        return []


def _dimension(x):
    """مطابقة تامة لاسم بُعد (أو "D10"/"10")، مش أي كلمة فرعية."""
    dims = _dimension_names()
    if not dims:
        return str(x or "")[:120]
    x = str(x or "").strip().lower()
    m = re.fullmatch(r"d?\s*(\d{1,2})", x)
    if m and 1 <= int(m.group(1)) <= len(dims):
        return dims[int(m.group(1)) - 1]
    x = re.sub(r"\s*\(.*?\)\s*", "", x).strip()
    return next((d for d in dims if d.lower() == x), next((d for d in dims if len(x) > 8 and d.lower() in x), ""))


def _cos(a, b):
    import math
    na, nb = math.sqrt(sum(v * v for v in a)), math.sqrt(sum(v * v for v in b))
    return sum(p * q for p, q in zip(a, b)) / (na * nb) if na and nb else 0.0


def _file_hash(paths):
    h = hashlib.sha256()
    for f in paths:
        try:
            h.update(f.name.encode() + f.read_bytes())
        except OSError:
            pass
    return h.hexdigest()[:12]


def _code_version():
    """بصمات لملفات governance/ والسيناريوهات وقائمة الوثائق وقاعدة المعرفة (قابلية إعادة الإنتاج)."""
    g = C.ROOT / "governance"
    return {"code": _file_hash(sorted(g.glob("*.py")) + sorted(g.glob("*.yaml"))),
            "scenarios": _file_hash(sorted(C.SCENARIO_DIR.glob("*.yaml"))),
            "manifest": _file_hash([C.POLICY_MANIFEST]), "kb_export": _file_hash([C.POLICY_EXPORT])}


STATUS_RANK = {"CONTINUE": 0, "CONTINUE_WITH_CONDITIONS": 1, "ESCALATE_TO_HUMAN": 2, "SUSPEND": 3, "ERROR": 4}

DECISION_RULES = [
    ("R1", "SUSPEND", "An authority agent issued BLOCK backed by at least one verified, relevant quote (8+ words) "
                      "from a binding UAE federal or emirate law or school policy (not guidance)."),
    ("R1b", "SUSPEND", "Precautionary suspension: an authority agent rated the risk HIGH and backed its assessment with "
                       "a verified, relevant quote (8+ words) from a binding UAE law or school policy, even though its "
                       "verdict was NEED_INFO or CONDITIONS. Lifted like R1 (see R5)."),
    ("R2", "ESCALATE_TO_HUMAN", "An authority agent needs information, an agent or retrieval failed, or a verdict was "
                                "unsupported by evidence."),
    ("R3", "CONTINUE_WITH_CONDITIONS", "At least one authority agent approved with conditions (all conditions are merged)."),
    ("R4", "CONTINUE", "All responding authority agents approved with verified, relevant evidence."),
    ("R0", "carry_over", "No authority agent responded in this stage; previous status is kept."),
    ("R5", "SUSPEND", "A suspension stays in force until every authority that issued it responds again with an "
                      "evidence-backed APPROVE or CONDITIONS."),
]
RULE_TEXT = {a: c for a, _, c in DECISION_RULES}


def _effective(responses):
    """لكل وكيل: أشد قرار أعطاه بالمرحلة (رد الجولة الثانية ما بيمحي إيقاف الجولة الأولى)."""
    eff = {}
    for r in responses:
        cur = eff.get(r["agent"])
        if cur is None or VERDICT_RANK.get(r["verdict"], 2) >= VERDICT_RANK.get(cur["verdict"], 2):
            eff[r["agent"]] = r
    return list(eff.values())


def decide(responses, previous="CONTINUE"):
    """قرار حتمي من ردود المرحلة (كل الردود، بالجولتين). بيرجع الحالة والقاعدة والشروط والأسئلة المفتوحة."""
    eff = _effective(responses)
    auth = [r for r in eff if r.get("_authority")]
    conditions, mitigations, open_q, review_notes = [], [], [], []
    for r in eff:
        target = mitigations if r.get("_role") == "solution" else conditions
        if r["verdict"] == "CONDITIONS" or r.get("_role") == "solution":
            for c in r.get("conditions", []):
                item = {"by": r["agent"], "condition": c}
                if any(n in c for n in r.get("unverified_numbers", [])):
                    item["needs_review"] = "contains a number not found in the sources"
                    review_notes.append(f"{r['agent']}: {c[:120]}")
                target.append(item)
    for r in responses:
        for q in r.get("questions", []):
            open_q.append({"from": r["agent"], **q})
    blocks = [r for r in auth if r["verdict"] == "BLOCK"
              and any(evidence.decisive(c, C.EVIDENCE_REL_MIN) for c in r.get("citations_verified", []))]
    # R1b: النموذج الصغير بيكتب "انتهاك" وخطر عالي وبيقتبس نص ملزم، وبرضه بيختار NEED_INFO. القاعدة الثابتة بتوقف احترازياً.
    precaution = []
    for r in responses:
        if (r.get("_authority") and r["verdict"] in ("NEED_INFO", "CONDITIONS") and r.get("risk") == "high"
                and any(evidence.decisive(c, C.EVIDENCE_REL_MIN) for c in r.get("citations_verified", []))
                and r["agent"] not in precaution):
            precaution.append(r["agent"])
    escal = [r for r in eff if (r.get("_authority") and r["verdict"] == "NEED_INFO")
             or {"agent_error", "retrieval_error", "unsupported_verdict", "unsupported_approval"} & set(r.get("flags", []))]
    if blocks:
        rule, status, basis = "R1", "SUSPEND", [r["agent"] for r in blocks]
    elif precaution:
        rule, status, basis = "R1b", "SUSPEND", precaution
    elif escal:
        rule, status, basis = "R2", "ESCALATE_TO_HUMAN", [r["agent"] for r in escal]
    elif any(r["verdict"] == "CONDITIONS" for r in auth):
        rule, status, basis = "R3", "CONTINUE_WITH_CONDITIONS", [r["agent"] for r in auth if r["verdict"] == "CONDITIONS"]
    elif auth:
        rule, status, basis = "R4", "CONTINUE", [r["agent"] for r in auth]
    else:
        rule, status, basis = "R0", previous, []
    return {"status": status, "rule": rule, "rule_text": RULE_TEXT[rule], "basis_agents": basis,
            "conditions": conditions, "proposed_mitigations": mitigations, "open_questions": open_q,
            "human_review_required": status in ("SUSPEND", "ESCALATE_TO_HUMAN") or bool(review_notes),
            "review_notes": review_notes,
            "votes": {r["agent"]: r["verdict"] for r in eff}}


def _lifts(r):
    """رد بيرفع الإيقاف: موافقة (أو بشروط) بدون أعطال، مع اقتباس موثّق ذو صلة."""
    return (r["verdict"] in ("APPROVE", "CONDITIONS") and not {"agent_error", "retrieval_error"} & set(r.get("flags", []))
            and any(evidence.is_relevant(c, C.EVIDENCE_REL_MIN) for c in r.get("citations_verified", [])))


GAP_SYSTEM = """You are the Policy & Legal Advisor writing a policy GAP ANALYSIS after a governance SIMULATION of an
AI tutor deployed in UAE schools. Compare what UAE texts say (passages U#) with international benchmarks
(passages B#). A gap is something the simulation exposed that UAE texts do not address, address only vaguely,
or address differently from benchmarks. Read every U# passage before claiming "missing": if a U# passage covers the
topic (e.g. consent, cross-border transfer, children), the status is "partial" or "ambiguous" and you must quote it.
U# passages tagged [free zone] (DIFC/ADGM) apply only inside those free zones: they can show a "partial" federal
picture but never make a gap "covered" for UAE schools in general. U# passages tagged [UAE guidance, non-binding]
(strategies, charters, guides) show policy intent: they can make a gap "partial" or "ambiguous", but say in the
description that no binding provision was found.
Rules: quote passages EXACTLY (8-40 words, machine-checked, never drop "not"/"no" or change numbers). If no U#
passage covers the issue, set uae_status to "missing" and leave uae_citations empty — do not invent provisions.
{lang_rule}
Return ONLY JSON: {{"gaps": [{{"title": "...", "description": "1-3 sentences", "uae_status": "missing|ambiguous|partial",
"uae_citations": [{{"ref": "U1", "quote": "..."}}], "benchmark_citations": [{{"ref": "B1", "quote": "..."}}],
"recommendation": "concrete policy or standard recommendation", "y3172_node": "ONE of: SRC, C, PP, M, P, D, SINK, MLFO, Sandbox",
"readiness_dimension": "ONE of: {dims}"}}]}}
Give 3 to 5 gaps, most important first."""


class RunAborted(Exception):
    pass


class Coordinator:
    def __init__(self, scenario, lang="en", listener=None, run_id=None, owner=None, max_seconds=None, cancel=None):
        self.sc = scenario
        self.lang = lang
        personas = load_personas()
        self.agents = {aid: Agent(aid, personas[aid], lang) for aid in ORDER if aid in personas}
        self.tainted = set()                    # أرقام مخترعة، مشتركة بين كل الوكلاء
        for a in self.agents.values():
            a.tainted = self.tainted
        self.run_id = run_id or new_run_id(scenario["id"])
        self.log = AuditLog(self.run_id, listener=listener)
        self.status = "CONTINUE"
        self.history = []
        self._decisions = []
        self._blockers = set()
        self.llm_calls = 0
        self.owner = owner
        self.max_seconds = max_seconds
        self.cancel = cancel            # threading.Event اختياري
        self._t0 = time.time()

    # ------------------------------------------------------------ helpers
    def _others(self, aid):
        return [a for a in self.agents if a != aid]

    def _check_budget(self):
        if self.cancel is not None and self.cancel.is_set():
            raise RunAborted("cancelled")
        if self.max_seconds and time.time() - self._t0 > self.max_seconds:
            raise RunAborted(f"time limit {self.max_seconds}s exceeded")

    def _call(self, agent, stage, focus):
        self._check_budget()
        r = agent.respond(self.sc["setup"], stage, focus, self._others(agent.id))
        r["_authority"], r["_role"] = agent.authority, agent.role
        self.llm_calls += 1
        rec = self.log.log("agent_response", agent.id, {k: v for k, v in r.items() if not k.startswith("_")})
        for q in r.get("questions", []):
            m = Message(agent.id, q["to"], "QUESTION", q["question"], stage, rec["seq"])
            self.agents[q["to"]].inbox.append(m)
            self.log.log("message", agent.id, m.to_dict())
        for a in r.get("messages", []):
            m = Message(agent.id, a["to"], "ANSWER" if self.agents[a["to"]].last and any(
                q.get("to") == agent.id for q in self.agents[a["to"]].last.get("questions", [])) else "NOTIFY",
                a["text"], stage, rec["seq"])
            self.agents[a["to"]].inbox.append(m)
            self.log.log("message", agent.id, m.to_dict())
        return r

    # ------------------------------------------------------------ main loop
    def run(self):
        self._t0 = time.time()
        self.log.log("run_start", "coordinator", {
            "scenario_id": self.sc["id"], "title": self.sc.get("title_en"), "title_ar": self.sc.get("title_ar"),
            "setup": self.sc["setup"], "owner": self.owner,
            "disclaimer": "Simulation: agents emulate institutional roles for testing and do not represent official positions.",
            "agents": {a: {"name_en": g.p["name_en"], "name_ar": g.p["name_ar"], "role": g.role, "authority": g.authority,
                           "categories": g.p.get("categories")} for a, g in self.agents.items()},
            "llm_provider": C.LLM_PROVIDER, "chat_model": C.GEMINI_MODEL if C.LLM_PROVIDER == "gemini" else C.CHAT_MODEL,
            "embed_model": C.EMBED_MODEL, "kb": retrieval.stats(), "lang": self.lang,
            "settings": {k: getattr(C, k) for k in ("POLICY_TOP_K", "POLICY_MAX_DIST", "EVIDENCE_REL_MIN", "GAP_ABSENCE_SIM",
                                                     "MAX_QUESTIONS", "PASSAGE_CHARS", "AGENT_MAX_TOKENS")},
            "code_version": _code_version(), "expected": self.sc.get("expected"),
            "decision_rules": [{"id": a, "status": b, "text": c} for a, b, c in DECISION_RULES]})
        gaps, error = [], None
        try:
            for st in self.sc["stages"]:
                self.run_stage(st)
            gaps = self.gap_analysis()
        except Exception as e:                       # أي عطل: بنسجّله وبنسكّر السجل صح بدل ما يضيع شغل ساعة
            error = f"{type(e).__name__}: {str(e)[:200]}"
            self.log.log("run_error", "coordinator", {"error": error})
        undelivered = [{"to": a.id, "from": m.sender, "kind": m.kind, "stage": m.stage}
                       for a in self.agents.values() for m in a.inbox]
        if undelivered:
            self.log.log("message_undelivered", "coordinator", {"messages": undelivered})
        verified = sum(len(r.get("citations_verified", [])) for r in self.history)
        rejected = sum(len(r.get("citations_rejected", [])) for r in self.history)
        worst = max((d["status"] for d in self._decisions), key=lambda s: STATUS_RANK.get(s, 0), default=self.status)
        final = "ERROR" if error else self.status
        self.log.log("run_end", "coordinator", {
            "final_status": final, "most_restrictive_status": worst, "stages": len(self.sc["stages"]),
            "stages_completed": len(self._decisions), "agent_calls": self.llm_calls, "citations_verified": verified,
            "citations_rejected": rejected, "gaps": len(gaps), "error": error,
            "expectations": self._score_expectations(worst), "duration_s": round(time.time() - self._t0, 1)})
        self.log.close()
        return self.run_id

    def _score_expectations(self, worst):
        """مقارنة النتيجة بالسلوك المتوقع المكتوب بالسيناريو (expected:)."""
        exp = self.sc.get("expected") or {}
        out = []
        if exp.get("min_final_status"):
            ok = worst != "ERROR" and STATUS_RANK.get(worst, 0) >= STATUS_RANK.get(exp["min_final_status"], 0)
            out.append({"check": f"most restrictive status >= {exp['min_final_status']}", "actual": worst, "pass": ok})
        for sid, want in (exp.get("stage_min_status") or {}).items():
            d = next((d for d in self._decisions if str(d["stage"]) == str(sid)), None)
            got = d["status"] if d else None
            out.append({"check": f"stage {sid} status >= {want}", "actual": got,
                        "pass": bool(got) and got != "ERROR" and STATUS_RANK.get(got, 0) >= STATUS_RANK.get(want, 0)})
        for aid, verdicts in (exp.get("agent_verdict_any") or {}).items():
            got = sorted({r["verdict"] for r in self.history if r["agent"] == aid})
            out.append({"check": f"{aid} gives one of {verdicts}", "actual": got, "pass": bool(set(got) & set(verdicts))})
        return out

    def run_stage(self, st):
        sid = st["id"]
        receivers = set()
        for rel in st.get("release", []):
            to = list(self.agents) if "all" in rel["to"] else [a for a in rel["to"] if a in self.agents]
            item = {"stage": sid, "info": rel["info_en"]}
            for a in to:
                self.agents[a].receive(item)
                receivers.add(a)
            self.log.log("release", "scenario", {"stage": sid, "title_en": st.get("title_en"), "title_ar": st.get("title_ar"),
                                                  "to": to, "info_en": rel["info_en"], "info_ar": rel.get("info_ar", "")})
        focus = st.get("focus", "")
        responses = []
        # جولة 1: الوكلاء اللي وصلتهم معلومة جديدة أو عندهم سؤال/إشعار
        for aid in ORDER:
            a = self.agents.get(aid)
            if a and (aid in receivers or a.needs_turn()):
                responses.append(self._call(a, sid, focus))
        # جولة 2 (مرة وحدة): اللي وصلهم سؤال، أو جهة رسمية وصلها جواب/إشعار
        for aid in ORDER:
            a = self.agents.get(aid)
            if a and a.needs_turn():
                responses.append(self._call(a, sid, focus))
        self.history += responses                     # كل الردود (مش بس الأخير لكل وكيل)
        d = decide(responses, self.status)
        responded = {r["agent"] for r in responses}
        if self.status == "SUSPEND" and d["status"] != "SUSPEND":
            # الإيقاف بينرفع بس إذا كل جهة أوقفت ردّت هالمرحلة بموافقة مدعومة بدليل
            lifted = {aid for aid in self._blockers if aid in responded
                      and all(_lifts(r) for r in responses if r["agent"] == aid)}
            if self._blockers - lifted:
                d.update(status="SUSPEND", rule="R5", basis_agents=sorted(self._blockers - lifted),
                         human_review_required=True, rule_text=RULE_TEXT["R5"])
            self._blockers -= lifted
        if d["status"] == "SUSPEND" and d["rule"] in ("R1", "R1b"):
            self._blockers |= set(d["basis_agents"])
        self.status = d["status"]
        d["stage"] = sid
        self._decisions.append(d)
        self.log.log("decision", "coordinator", d)

    # ------------------------------------------------------------ gap analysis
    def gap_analysis(self):
        self._check_budget()
        issues = " ".join(st.get("focus", "") for st in self.sc["stages"])
        topics = self.sc.get("gap_queries") or [issues]
        try:
            uae = retrieval.merge_hits(*[retrieval.search_policy(q, categories=C.UAE_CATEGORIES, k=3) for q in topics], limit=6)
            bench = retrieval.merge_hits(*[retrieval.search_policy(q, categories=["International_Benchmarks"], k=3)
                                           for q in topics], limit=4)
        except Exception as e:
            self.log.log("gap_analysis", "policy_advisor", {"error": f"retrieval: {type(e).__name__}", "gaps": []})
            return []
        summary = "\n".join(f"- Stage {d['stage']}: {d['status']} ({d['rule']}); votes {d['votes']}; "
                            f"open questions: {[q['question'][:120] for q in d['open_questions']]}" for d in self._decisions)
        assessments = "\n".join(f"- {r['agent']} (stage {r['stage']}, {r['verdict']}): {r.get('assessment', '')[:180]}"
                                for r in self.history)[:3500]
        user = (f"CASE:\n{self.sc['setup']}\n\nSIMULATION OUTCOME:\n{summary}\n\nAGENT ASSESSMENTS:\n{assessments}\n\n"
                f"UAE PASSAGES:\n{format_passages(uae, 'U', 700)}\n\nBENCHMARK PASSAGES:\n{format_passages(bench, 'B', 700)}")
        system = GAP_SYSTEM.format(dims=", ".join(_dimension_names()) or "AI & Policies",
                                   lang_rule={"ar": "Write titles, descriptions and recommendations in Arabic."}.get(self.lang, "Write in English."))
        try:
            data, meta = llm.chat_json([{"role": "system", "content": system}, {"role": "user", "content": user}], max_tokens=1600)
            self.llm_calls += 1
        except Exception as e:
            self.log.log("gap_analysis", "policy_advisor", {"error": type(e).__name__, "gaps": []})
            return []
        raw = data.get("gaps") if isinstance(data, dict) else None
        gaps = []
        for g in (raw if isinstance(raw, list) else [])[:6]:
            if not isinstance(g, dict) or not g.get("title"):
                continue
            uv, ur = evidence.verify_citations([{"ref": c.get("ref", ""), "quote": c.get("quote")}
                                                for c in g.get("uae_citations") or [] if isinstance(c, dict)], uae, visible_chars=700)
            bv, br = evidence.verify_citations([{"ref": c.get("ref", ""), "quote": c.get("quote")}
                                                for c in g.get("benchmark_citations") or [] if isinstance(c, dict)], bench, visible_chars=700)
            gap_text = f"{g['title']}. {g.get('description', '')}"
            gap_known = " ".join([self.sc["setup"], " ".join(rel.get("info_en", "") for st in self.sc["stages"] for rel in st.get("release", [])),
                                  " ".join(h["text"] for h in uae + bench)])
            gap_unverified = unverified_numbers(f"{gap_text} {g.get('recommendation', '')}", gap_known)
            evidence.score_relevance(uv, gap_text)
            evidence.score_relevance(bv, gap_text)
            uv_rel = [c for c in uv if evidence.is_relevant(c, C.EVIDENCE_REL_MIN)]
            bv_rel = [c for c in bv if evidence.is_relevant(c, C.EVIDENCE_REL_MIN)]
            status = str(g.get("uae_status", "ambiguous")).lower()
            # فحص الغياب: إذا الوكيل قال "ما في نص إماراتي" بنقارن الفجوة بالمقاطع الإماراتية اللي انعرضت عليه.
            absence = {"uae_passages_searched": len(uae), "closest_uae_dist": min((h["dist"] for h in uae), default=None)}
            if status == "missing" and uae:
                try:
                    vecs = retrieval.embed_many([gap_text[:1000]] + [h["text"][:1500] for h in uae])
                    sims = sorted(((round(_cos(vecs[0], v), 3), h) for v, h in zip(vecs[1:], uae)), key=lambda x: -x[0])
                    absence["closest"] = [{"sim": s_, "title": h["meta"].get("title"), "article": h["meta"].get("article"),
                                           "chunk_id": h["id"]} for s_, h in sims[:2]]
                    absence["possible_uae_provision"] = bool(sims and sims[0][0] >= C.GAP_ABSENCE_SIM)
                except Exception as e:
                    absence["error"] = type(e).__name__
                    absence["possible_uae_provision"] = True     # ما قدرنا نتحقق => مراجعة بشرية
            gaps.append({"title": str(g["title"])[:200], "description": str(g.get("description", ""))[:800],
                         "uae_status": status if status in ("missing", "ambiguous", "partial") else "ambiguous",
                         "uae_citations_verified": uv, "uae_citations_rejected": ur,
                         "benchmark_citations_verified": bv, "benchmark_citations_rejected": br,
                         "recommendation": str(g.get("recommendation", ""))[:600],
                         "y3172_node": _node(g.get("y3172_node")),
                         "readiness_dimension": _dimension(g.get("readiness_dimension")),
                         "evidence_level": ("benchmark+uae" if bv_rel and uv_rel else "benchmark" if bv_rel
                                            else "uae" if uv_rel else "low_relevance" if (uv or bv) else "unverified"),
                         "absence_check": absence if status == "missing" else None,
                         "unverified_numbers": gap_unverified})
        self.log.log("gap_analysis", "policy_advisor", {"gaps": gaps, "llm": meta,
                                                       "uae_hits": [h["id"] for h in uae], "benchmark_hits": [h["id"] for h in bench]})
        return gaps
