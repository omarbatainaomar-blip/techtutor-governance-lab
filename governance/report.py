"""تحويل سجل التدقيق لتقرير Markdown (مفيد للتقرير التقني وللفيديو). متسامح مع السجلات القديمة أو الناقصة."""
from .audit import is_complete, verify_chain

STATUS_AR = {"CONTINUE": "استمرار", "CONTINUE_WITH_CONDITIONS": "استمرار بشروط",
             "ESCALATE_TO_HUMAN": "تصعيد لمراجعة بشرية", "SUSPEND": "إيقاف", "ERROR": "خطأ"}
DOWNGRADE_WHY = {"low_relevance_evidence": "the quoted text is not relevant enough to the issue",
                 "non_binding_or_short_evidence": "a suspension needs an 8+ word quote from a binding UAE law or school policy (not guidance, free zone or international)",
                 "unsupported_approval": "an approval needs at least one verified quote",
                 "unsupported_verdict": "no verified citation"}


def _cite(c):
    loc = []
    if c.get("page") not in (None, -1, ""):
        loc.append(f"p.{c['page']}")
    if c.get("article"):
        loc.append(f"Art. {c['article']}")
    if c.get("binding_scope"):
        loc.append(c["binding_scope"])
    if c.get("relevance") is not None:
        loc.append(f"relevance {c['relevance']}")
    text = c.get("source_span") or c.get("quote", "")         # نص المصدر الفعلي، مش صياغة الوكيل
    return f"> \"{text}\"  \n> — *{c.get('title')}*{(' (' + ', '.join(loc) + ')') if loc else ''}"


def render(records):
    ok, bad = verify_chain(records)
    start = next((r for r in records if r.get("type") == "run_start"), {"payload": {}}).get("payload") or {}
    end = next((r for r in records if r.get("type") == "run_end"), {"payload": {}}).get("payload") or {}
    names = {a: (v or {}).get("name_en", a) for a, v in (start.get("agents") or {}).items()}
    head = records[-1].get("hash") if records else None
    L = [f"# Governance run: {start.get('title')}", "",
         "> Simulation for testing AI governance. Agents emulate institutional roles and do not represent official positions.", "",
         f"- Run ID: `{records[0].get('run_id') if records else '?'}`",
         f"- Model: {start.get('llm_provider')} / {start.get('chat_model')} · embeddings: {start.get('embed_model')}",
         f"- Knowledge base: {start.get('kb')} · versions: {start.get('code_version')}",
         f"- Audit chain: {'✅ intact (' + str(len(records)) + ' events)' if ok else '❌ broken at event ' + str(bad)}"
         f"{'' if is_complete(records) else ' · ⚠️ run incomplete'} · head hash `{(head or '')[:16]}`",
         f"- Final status: **{end.get('final_status')}** · most restrictive: **{end.get('most_restrictive_status')}**",
         f"- Agent calls: {end.get('agent_calls')} · verified citations: {end.get('citations_verified')} · "
         f"rejected citations: {end.get('citations_rejected')} · duration: {end.get('duration_s')} s",
         f"- Settings: {start.get('settings', {})}", ""]
    if end.get("error"):
        L += [f"**Run error:** {end['error']}", ""]
    if end.get("expectations"):
        L += ["## Expected behaviour checks", ""] + [f"- {'✅' if e.get('pass') else '❌'} {e.get('check')} (actual: {e.get('actual')})"
                                                    for e in end["expectations"]] + [""]
    L += ["## Case", "", start.get("setup", ""), ""]
    for r in records:
        p = r.get("payload") or {}
        t = r.get("type")
        if t == "release":
            L += [f"## Stage {p.get('stage')}: {p.get('title_en')}", "",
                  f"**Information released to:** {', '.join(names.get(a, a) for a in p.get('to', []))}  ", f"{p.get('info_en', '')}", ""]
        elif t == "agent_response":
            L += [f"### {names.get(r.get('actor'), r.get('actor'))} → **{p.get('verdict')}** (risk: {p.get('risk')})"
                  + (f" · flags: {', '.join(p['flags'])}" if p.get("flags") else ""), "", p.get("assessment", ""), ""]
            if p.get("verdict_original"):
                why = next((DOWNGRADE_WHY[f] for f in p.get("flags", []) if f in DOWNGRADE_WHY), "insufficient evidence")
                L += [f"*Original verdict {p['verdict_original']} was changed to {p.get('verdict')}: {why}.*", ""]
            if p.get("unverified_numbers"):
                L += [f"*⚠️ Numbers not found in the case, messages or cited text (possible hallucination): {', '.join(p['unverified_numbers'])}*", ""]
            for c in p.get("conditions", []):
                L.append(f"- Condition/mitigation: {c}")
            for c in p.get("citations_verified", []):
                L += ["", _cite(c)]
            for c in p.get("citations_rejected", []):
                L.append(f"- ❌ rejected quote ({c.get('reason')}): \"{str(c.get('quote', ''))[:160]}\"")
            if p.get("rationale"):
                L += ["", "<details><summary>Reasoning trace</summary>", ""] + [f"{i}. {s}" for i, s in enumerate(p["rationale"], 1)] + ["", "</details>"]
            L.append("")
        elif t == "message":
            L += [f"- ✉️ {p.get('kind')} {names.get(p.get('sender'), p.get('sender'))} → {names.get(p.get('recipient'), p.get('recipient'))}: {p.get('content')}", ""]
        elif t == "decision":
            L += [f"#### Coordinator decision (stage {p.get('stage')}): **{p.get('status')}** — rule {p.get('rule')}", "",
                  f"{p.get('rule_text', '')}  ", f"Votes: {p.get('votes')}"
                  + ("  \n⚠️ Human review required." if p.get("human_review_required") else ""), ""]
            for n in p.get("review_notes", []):
                L.append(f"- ⚠️ condition with an unverified number: {n}")
        elif t == "gap_analysis":
            L += ["## Policy gap analysis", ""]
            if p.get("error"):
                L += [f"*Gap analysis failed: {p['error']}*", ""]
            for i, g in enumerate(p.get("gaps", []), 1):
                L += [f"### Gap {i}: {g.get('title')}", "", g.get("description", ""), "",
                      f"- UAE status: **{g.get('uae_status')}** · evidence: {g.get('evidence_level')} · Y.3172 node: {g.get('y3172_node')} · "
                      f"readiness dimension: {g.get('readiness_dimension')}",
                      f"- Recommendation: {g.get('recommendation')}"]
                if g.get("unverified_numbers"):
                    L.append(f"- ⚠️ Number(s) not found in the case or passages (needs human review): {', '.join(g['unverified_numbers'])}")
                ab = g.get("absence_check") or {}
                if ab:
                    L.append(f"- Absence check: {ab.get('uae_passages_searched')} UAE passages searched, closest distance {ab.get('closest_uae_dist')}")
                    if ab.get("possible_uae_provision"):
                        L.append("- ⚠️ Needs human review: a UAE passage may cover this ("
                                 + ", ".join(str(c.get("title")) + (" Art. " + c["article"] if c.get("article") else "")
                                             for c in ab.get("closest", [])) + ")")
                for c in g.get("uae_citations_verified", []) + g.get("benchmark_citations_verified", []):
                    L += ["", _cite(c)]
                L.append("")
        elif t in ("run_error", "message_undelivered"):
            L += [f"- ⚠️ {t}: {p}", ""]
    return "\n".join(L)
