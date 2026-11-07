"use strict";
/* Governance Lab: تشغيل سيناريوهات الوكلاء وإعادة عرض سجلات التدقيق. كل النصوص بتنعرض بـ textContent (بدون innerHTML). */
const $ = id => document.getElementById(id);
const LS = {
  get(k) { try { return JSON.parse(localStorage.getItem(k)); } catch (_) { return null; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (_) {} }
};
let lang = LS.get("lang") || "ar", theme = LS.get("theme") || "dark";
let scen = [], runs = [], agents = {}, current = null, replayTimer = null, busy = false, info = null;

const T = {
  ar: {
    back: "← العودة للمحادثة", scen: "السيناريوهات (أعطال متدرّجة)", runs: "التشغيلات السابقة (سجل التدقيق)",
    run: "تشغيل", out_en: "مخرجات EN", out_ar: "مخرجات AR", replay: "إعادة عرض", stages: "مراحل",
    dl_md: "تقرير MD", dl_log: "سجل JSONL", chain_ok: "🔗 السجل سليم", chain_bad: "⚠️ السجل معدَّل",
    empty: "اختر سيناريو وشغّله، أو اختر تشغيلاً سابقاً لإعادة عرضه.",
    running: "⏳ الوكلاء يعملون… كل رد قد يأخذ دقيقة على المعالج.", to: "وصلت المعلومة إلى:", only: "معلومة جزئية",
    stage: "المرحلة", decision: "قرار المنسّق", rule: "القاعدة", human: "⚠️ يتطلب مراجعة بشرية قبل التنفيذ",
    cond: "شروط / إجراءات", rationale: "مسار الاستدلال", rejected: "اقتباس مرفوض", downgraded: "تم تخفيض القرار: لا يوجد دليل موثّق",
    gaps: "تحليل فجوات السياسات", g_title: "الفجوة", g_status: "الوضع في الإمارات", g_rec: "التوصية", g_ev: "الدليل",
    final: "النتيجة النهائية", calls: "استدعاءات الوكلاء", cv: "اقتباسات موثّقة", cr: "اقتباسات مرفوضة", dur: "المدة (ث)",
    login: "سجّل الدخول بحساب (مش ضيف) لتشغيل السيناريوهات", busy: "في سيناريو شغال حالياً، استنى يخلص", notAllowed: "حسابك مش مسموح له يشغّل سيناريوهات (GOV_RUNNERS)", rate: "وصلت الحد، جرّب بعد شوي",
    failed: "تعذّر إكمال التشغيل", case: "الحالة", kb: "قاعدة المعرفة",
    status: { CONTINUE: "استمرار", CONTINUE_WITH_CONDITIONS: "استمرار بشروط", ESCALATE_TO_HUMAN: "تصعيد لإنسان", SUSPEND: "إيقاف" },
    verdict: { APPROVE: "موافقة", CONDITIONS: "موافقة بشروط", BLOCK: "إيقاف", NEED_INFO: "يحتاج معلومات" },
    uae: { missing: "غير موجود", ambiguous: "غامض", partial: "جزئي" }
  },
  en: {
    back: "← Back to chat", scen: "Scenarios (progressive errors)", runs: "Previous runs (audit log)",
    run: "Run", out_en: "EN output", out_ar: "AR output", replay: "Replay", stages: "stages",
    dl_md: "MD report", dl_log: "JSONL log", chain_ok: "🔗 Audit chain intact", chain_bad: "⚠️ Audit chain broken",
    empty: "Pick a scenario and run it, or choose a previous run to replay.",
    running: "⏳ Agents are working… each reply can take a minute on CPU.", to: "Released to:", only: "partial information",
    stage: "Stage", decision: "Coordinator decision", rule: "Rule", human: "⚠️ Human review required before acting",
    cond: "Conditions / mitigations", rationale: "Reasoning trace", rejected: "Rejected quote", downgraded: "Verdict downgraded: no verified evidence",
    gaps: "Policy gap analysis", g_title: "Gap", g_status: "UAE status", g_rec: "Recommendation", g_ev: "Evidence",
    final: "Final outcome", calls: "Agent calls", cv: "Verified quotes", cr: "Rejected quotes", dur: "Duration (s)",
    login: "Sign in with an account (not guest) to run scenarios", busy: "A scenario is already running, please wait", notAllowed: "Your account is not allowed to run scenarios (GOV_RUNNERS)", rate: "Rate limit reached, try later",
    failed: "The run could not be completed", case: "Case", kb: "Knowledge base",
    status: { CONTINUE: "Continue", CONTINUE_WITH_CONDITIONS: "Continue with conditions", ESCALATE_TO_HUMAN: "Escalate to human", SUSPEND: "Suspend" },
    verdict: { APPROVE: "Approve", CONDITIONS: "Conditions", BLOCK: "Block", NEED_INFO: "Need info" },
    uae: { missing: "missing", ambiguous: "ambiguous", partial: "partial" }
  }
};
const t = k => T[lang][k];
const COLORS = { tutor: "#4f8cff", policy_advisor: "#7c5cff", data_office: "#0ea5a4", moe: "#e11d48", ai_office: "#f59e0b" };
const ICONS = { tutor: "🤖", policy_advisor: "⚖", data_office: "🔒", moe: "🎓", ai_office: "🏛" };

function el(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined && text !== null) {
    e.textContent = text;
    if (["p", "q", "li", "td", "div", "b", "span"].includes(tag)) e.dir = "auto";   // كل نص باتجاه لغته (عربي/إنجليزي)
  }
  return e;
}
function agentName(id) { const a = agents[id]; return a ? (lang === "ar" ? a.name_ar : a.name_en) : id; }
function avatar(id) { const a = el("span", "av", ICONS[id] || "•"); a.style.background = COLORS[id] || "#555"; return a; }

async function api(path, method = "GET", body) {
  const r = await fetch(path, { method, credentials: "same-origin",
    headers: body ? { "Content-Type": "application/json" } : {}, body: body ? JSON.stringify(body) : undefined });
  let data = {}; try { data = await r.json(); } catch (_) {}
  return { ok: r.ok, status: r.status, data };
}

/* ---------------- sidebar ---------------- */
function applyUI() {
  const r = document.documentElement; r.lang = lang; r.dir = lang === "ar" ? "rtl" : "ltr"; r.dataset.theme = theme;
  document.querySelectorAll("[data-i]").forEach(e => e.textContent = t(e.dataset.i));
  $("glang").textContent = lang === "ar" ? "English" : "عربي";
  if (info) $("ginfo").textContent = `LLM: ${info.provider}/${info.chat_model} · embed: ${info.embed_model} · ${t("kb")}: ${JSON.stringify(info.kb)}`;
  renderScen(); renderRuns();
  if (current && current.chain_ok !== undefined) setChain(current.chain_ok);
  if (current) renderAll(current.events, false);
  else { $("tl").replaceChildren(el("div", "empty", t("empty"))); $("gtitle").textContent = "TechTutor Governance Lab"; }
}
$("glang").onclick = () => { lang = lang === "ar" ? "en" : "ar"; LS.set("lang", lang); applyUI(); };
$("gtheme").onclick = () => { theme = theme === "dark" ? "light" : "dark"; LS.set("theme", theme); document.documentElement.dataset.theme = theme; };

function renderScen() {
  const box = $("scen"); box.replaceChildren();
  scen.forEach(s => {
    const c = el("div", "scard");
    c.append(el("b", "", lang === "ar" ? (s.title_ar || s.title_en) : s.title_en));
    c.append(el("p", "", lang === "ar" ? (s.summary_ar || s.summary_en) : s.summary_en));
    const chips = el("div", "chips");
    (s.stages || []).forEach(st => chips.append(el("span", "chip",
      `${st.id}. ${lang === "ar" ? (st.title_ar || st.title_en) : st.title_en} → ${st.to.map(a => ICONS[a] || (a === "all" ? "👥" : a)).join("")}`)));
    c.append(chips);
    const row = el("div", "srow");
    const sel = el("select"); [["en", t("out_en")], ["ar", t("out_ar")]].forEach(([v, l]) => { const o = el("option", "", l); o.value = v; sel.append(o); });
    sel.value = lang;
    const b = el("button", "newbtn", "▶ " + t("run")); b.disabled = busy;
    b.onclick = () => runScenario(s.id, sel.value);
    row.append(b, sel); c.append(row); box.append(c);
  });
}
function renderRuns() {
  const box = $("runs"); box.replaceChildren();
  runs.forEach(r => {
    const it = el("div", "ritem" + (current && current.run_id === r.run_id ? " on" : ""));
    it.append(el("span", "", (r.final ? (t("status")[r.final] || r.final) + " · " : "") + (r.title || r.scenario)));
    it.append(el("small", "", `${r.run_id} · ${r.events} events`));
    it.onclick = () => openRun(r.run_id, true);
    box.append(it);
  });
}
async function loadSide() {
  const [s, inf] = await Promise.all([api("/api/gov/scenarios"), api("/api/gov/info")]);
  scen = (s.data.scenarios || []).filter(x => !x.error);
  if (inf.ok) info = inf.data;
  const r = await api("/api/gov/runs");
  runs = r.ok ? (r.data.runs || []) : [];
  if (r.status === 401) await api("/api/guest", "POST", {}).then(() => api("/api/gov/runs")).then(x => { runs = x.ok ? x.data.runs || [] : []; });
  applyUI();
}

/* ---------------- timeline ---------------- */
function header(events) {
  const start = events.find(e => e.type === "run_start");
  if (start) {
    agents = start.payload.agents || agents;
    $("gtitle").textContent = lang === "ar" ? (start.payload.title_ar || start.payload.title) : start.payload.title;
    const lg = $("legend"); lg.replaceChildren();
    Object.keys(agents).forEach(id => { const x = el("span", "lg"); x.append(avatar(id), el("span", "", agentName(id) + (agents[id].authority ? " ★" : ""))); lg.append(x); });
  }
}
function citeBox(c, bad) {
  const b = el("div", "cite" + (bad ? " bad" : ""));
  b.append(el("q", "", c.source_span || c.quote));          // نص المصدر الفعلي (مش صياغة الوكيل)
  if (bad) b.append(el("small", "", `${t("rejected")} · ${c.reason} · score ${c.best_score}`));
  else {
    const loc = [c.title, c.issuer, (c.page !== undefined && c.page !== -1 && c.page !== "") ? "p." + c.page : "", c.article ? "Art. " + c.article : "",
      (c.relevance !== undefined && c.relevance !== null) ? "rel " + c.relevance : ""].filter(Boolean).join(" · ");
    const s = el("small", "", loc);
    if (c.url && /^https?:\/\//.test(c.url)) { const a = el("a", "", " ↗"); a.href = c.url; a.target = "_blank"; a.rel = "noopener noreferrer"; s.append(a); }
    b.append(s);
  }
  return b;
}
function renderEvent(e) {
  const p = e.payload, tl = $("tl");
  if (e.type === "run_start") {
    const c = el("div", "ev"); c.append(el("b", "", t("case"))); c.append(el("p", "", p.setup)); tl.append(c);
  } else if (e.type === "release") {
    if (!tl.querySelector(`[data-stage="${p.stage}"]`)) {
      const s = el("div", "stage", `${t("stage")} ${p.stage}: ${lang === "ar" ? (p.title_ar || p.title_en) : p.title_en}`);
      s.dataset.stage = p.stage; tl.append(s);
    }
    const c = el("div", "ev rel"), h = el("div", "h");
    h.append(el("span", "", "📨"), el("span", "to", t("to")));
    p.to.forEach(a => h.append(avatar(a)));
    if (Object.keys(agents).length && p.to.length < Object.keys(agents).length) h.append(el("span", "secret", t("only")));
    c.append(h, el("p", "", lang === "ar" && p.info_ar ? p.info_ar : p.info_en)); tl.append(c);
  } else if (e.type === "agent_response") {
    const c = el("div", "ev"), h = el("div", "h");
    h.append(avatar(e.actor), el("span", "who", agentName(e.actor)), el("span", "sp"));
    h.append(el("span", "vb v-" + p.verdict, t("verdict")[p.verdict] || p.verdict), el("span", "risk", "risk: " + p.risk));
    (p.flags || []).forEach(f => h.append(el("span", "flag", f)));
    if (p.llm && p.llm.latency_s) h.append(el("span", "risk", p.llm.latency_s + "s"));
    c.append(h, el("p", "", p.assessment));
    if (p.verdict_original) c.append(el("p", "flag", `${t("downgraded")} (${p.verdict_original} → ${p.verdict})`));
    if (p.unverified_numbers && p.unverified_numbers.length) c.append(el("p", "flag", (lang === "ar" ? "⚠️ أرقام غير موجودة بالمعلومات أو الاقتباسات: " : "⚠️ Numbers not found in the case or quotes: ") + p.unverified_numbers.join(", ")));
    if (p.conditions && p.conditions.length) { const ul = el("ul", "cond"); p.conditions.forEach(x => ul.append(el("li", "", x))); c.append(el("small", "risk", t("cond")), ul); }
    (p.citations_verified || []).forEach(x => c.append(citeBox(x, false)));
    (p.citations_rejected || []).forEach(x => c.append(citeBox(x, true)));
    if (p.rationale && p.rationale.length) {
      const d = el("details"); d.append(el("summary", "", t("rationale")));
      const ol = el("ol"); p.rationale.forEach(x => ol.append(el("li", "", x))); d.append(ol); c.append(d);
    }
    tl.append(c);
  } else if (e.type === "message") {
    const m = el("div", "msg");
    m.append(el("span", "", p.kind === "QUESTION" ? "❓" : p.kind === "NOTIFY" ? "📣" : "↩"), avatar(p.sender), el("span", "", "→"), avatar(p.recipient));
    const tx = el("span"); tx.append(el("b", "", agentName(p.recipient) + ": "), document.createTextNode(p.content)); m.append(tx);
    tl.append(m);
  } else if (e.type === "decision") {
    const c = el("div", "ev dec"), h = el("div", "h");
    h.append(el("span", "", "⚖️"), el("span", "who", `${t("decision")} — ${t("stage")} ${p.stage}`), el("span", "sp"),
      el("span", "vb s-" + p.status, t("status")[p.status] || p.status));
    c.append(h, el("p", "rule", `${t("rule")} ${p.rule}: ${p.rule_text}`));
    if (p.human_review_required) c.append(el("span", "human", t("human")));
    tl.append(c);
  } else if (e.type === "gap_analysis") {
    const c = el("div", "ev gaps"); c.append(el("b", "", "🧭 " + t("gaps")));
    const tb = el("table"), hr = el("tr");
    [t("g_title"), t("g_status"), t("g_rec"), t("g_ev")].forEach(x => hr.append(el("th", "", x))); tb.append(hr);
    (p.gaps || []).forEach(g => {
      const tr = el("tr"), td1 = el("td");
      td1.append(el("b", "", g.title), el("div", "risk", g.description));
      [...(g.uae_citations_verified || []), ...(g.benchmark_citations_verified || [])].forEach(x => td1.append(citeBox(x, false)));
      if (g.absence_check && g.absence_check.possible_uae_provision) td1.append(el("div", "flag", lang === "ar" ? "⚠️ ممكن يكون في نص إماراتي يغطيها: يحتاج مراجعة بشرية" : "⚠️ A UAE provision may cover this: needs human review"));
      const td4 = el("td"); td4.append(el("span", "lvl", g.evidence_level), el("div", "risk", [g.y3172_node && "Y.3172: " + g.y3172_node, g.readiness_dimension].filter(Boolean).join(" · ")));
      tr.append(td1, el("td", "", t("uae")[g.uae_status] || g.uae_status), el("td", "", g.recommendation), td4); tb.append(tr);
    });
    c.append(tb); tl.append(c);
  } else if (e.type === "run_end") {
    const c = el("div", "ev"), s = el("div", "sum");
    const box = (v, l) => { const d = el("div"); d.append(el("b", "", v), el("small", "", l)); return d; };
    s.append(box(t("status")[p.final_status] || p.final_status, t("final")), box(p.agent_calls, t("calls")),
      box(p.citations_verified, t("cv")), box(p.citations_rejected, t("cr")), box(p.duration_s, t("dur")));
    c.append(s); tl.append(c);
    setStatus(p.most_restrictive_status || p.final_status);
  }
  const box = $("tl"); box.scrollTop = box.scrollHeight;
}
function setStatus(st) {
  const s = $("gstatus"); s.hidden = !st; s.className = "pill s-" + st; s.textContent = t("status")[st] || st;
}
function setChain(ok) {
  const c = $("gchain"); c.hidden = ok === null; c.className = "pill " + (ok ? "ok" : "bad"); c.textContent = ok ? t("chain_ok") : t("chain_bad");
}
function renderAll(events, animate) {
  clearTimeout(replayTimer);
  $("tl").replaceChildren(); header(events);
  const dec = events.filter(e => e.type === "decision");
  setStatus(dec.length ? dec[dec.length - 1].payload.status : null);
  if (!animate) { events.forEach(renderEvent); return; }
  let i = 0;
  const step = () => { if (i < events.length) { renderEvent(events[i++]); replayTimer = setTimeout(step, 450); } };
  step();
}
async function openRun(id, animate) {
  const r = await api("/api/gov/runs/" + encodeURIComponent(id));
  if (!r.ok) return;
  current = r.data;
  setChain(r.data.chain_ok);
  $("dlmd").hidden = $("dljsonl").hidden = false;
  $("dlmd").href = `/api/gov/runs/${encodeURIComponent(id)}.md`;
  $("dljsonl").href = `/api/gov/runs/${encodeURIComponent(id)}.jsonl`;
  renderRuns(); renderAll(current.events, animate);
}

/* ---------------- live run ---------------- */
async function runScenario(id, outLang) {
  if (busy) return;
  busy = true; renderScen(); clearTimeout(replayTimer);
  current = { run_id: null, events: [] };
  $("tl").replaceChildren(el("div", "running", t("running")));
  setChain(null); $("dlmd").hidden = $("dljsonl").hidden = true; $("gstatus").hidden = true;
  let err = null;
  try {
    const r = await fetch("/api/gov/run", { method: "POST", credentials: "same-origin",
      headers: { "Content-Type": "application/json" }, body: JSON.stringify({ scenario: id, lang: outLang }) });
    if (!r.ok) {
      let d = {}; try { d = await r.json(); } catch (_) {}
      err = d.error === "login_required" || r.status === 401 ? t("login") : d.error === "busy" ? t("busy") : d.error === "not_allowed" ? t("notAllowed") : d.error === "rate" ? t("rate") : t("failed");
    } else {
      const reader = r.body.getReader(), dec = new TextDecoder(); let buf = "", first = true;
      for (;;) {
        const { value, done } = await reader.read(); if (done) break;
        buf += dec.decode(value, { stream: true });
        let nl;
        while ((nl = buf.indexOf("\n")) >= 0) {
          const line = buf.slice(0, nl).trim(); buf = buf.slice(nl + 1); if (!line) continue;
          const msg = JSON.parse(line);
          if (msg.t === "event") {
            if (first) { $("tl").replaceChildren(); first = false; }
            current.events.push(msg.v); current.run_id = msg.v.run_id;
            if (msg.v.type === "run_start") header(current.events);
            renderEvent(msg.v);
            if (msg.v.type === "decision") setStatus(msg.v.payload.status);
          } else if (msg.t === "error") err = t("failed");
          else if (msg.t === "done") current.run_id = msg.v;
        }
      }
    }
  } catch (_) { err = t("failed"); }
  busy = false;
  if (err) $("tl").append(el("div", "running", "⚠️ " + err));
  const rr = await api("/api/gov/runs"); runs = rr.ok ? rr.data.runs || [] : runs;
  renderScen();
  if (current.run_id && !err) await openRun(current.run_id, false); else renderRuns();
}

document.documentElement.dataset.theme = theme;
loadSide();
