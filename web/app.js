"use strict";
const $ = id => document.getElementById(id);
const LS = {
  get(k) { try { return JSON.parse(localStorage.getItem(k)); } catch (_) { return null; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (_) {} }
};
let lang = LS.get("lang") || "ar", theme = LS.get("theme") || "dark";

const T = {
ar: {
  sub_login: "سجّل الدخول للمتابعة", sub_reg: "أنشئ حسابك الجديد", email: "البريد الإلكتروني", pass: "كلمة المرور (8 أحرف على الأقل)",
  login: "تسجيل الدخول", register: "إنشاء حساب", no_acc: "ليس لديك حساب؟ أنشئ حساباً", has_acc: "لديك حساب؟ سجّل الدخول",
  guest: "المتابعة كضيف", or: "أو",
  sec: "🔒 كلمات المرور مشفّرة على الخادم، وتنتهي الجلسة تلقائياً بعد 30 دقيقة من الخمول",
  new: "محادثة جديدة +", newchat: "محادثة جديدة", hist: "المحادثات السابقة", tasks: "المهام المجدولة", share: "مشاركة", send: "إرسال",
  pause: "إيقاف مؤقت ⏸", resume: "استئناف ▶", cancel: "إلغاء الرد", ph: "اكتب رسالتك بالعربية أو English…",
  logout: "خروج", signin: "تسجيل الدخول", guestname: "ضيف", hello: "كيف أساعدك اليوم؟",
  chips: ["اشرح لي مفهوماً", "ما الفرق بين TCP و UDP؟", "How does RAG work?"],
  e_email: "أدخل بريداً إلكترونياً صحيحاً", e_pw: "كلمة المرور 8 أحرف على الأقل وتحتوي حروفاً وأرقاماً", e_exists: "هذا البريد مسجّل مسبقاً",
  e_bad: "البريد أو كلمة المرور غير صحيحة", e_lock: "محاولات كثيرة. أعد المحاولة بعد ثوانٍ: ", e_net: "تعذّر الاتصال بالخادم",
  e_rate: "طلبات كثيرة، انتظر قليلاً ثم أعد المحاولة", e_busy: "هناك رد قيد التجهيز، انتظر انتهاءه",
  e_ollama: "تنبيه: Ollama غير متصل، لن تعمل الردود حتى تشغّله",
  pausedmsg: "⏸ الرد يُجهَّز في الخلفية وسيظهر عند الانتهاء…", ready: "وصل الرد على رسالتك ✅", stopped: "تم الإيقاف.",
  failed: "تعذّر إكمال الرد.", notasks: "لا توجد مهام مجدولة", t_ph: "ماذا تريد من المساعد أن ينفّذ؟", once: "مرة واحدة", daily: "كل يوم",
  add: "إضافة مهمة", t_bad: "اكتب المهمة وحدّد وقتاً مستقبلياً", t_note: "تُنفَّذ المهام أثناء فتح الصفحة فقط", t_ran: "تم تنفيذ مهمة مجدولة ⏰",
  copy: "نسخ", save: "حفظ كملف", copied: "تم نسخ المحادثة", nothing: "لا يوجد ما يُشارَك بعد", set: "الإعدادات", acc: "معلومات الحساب",
  member: "مستخدم مسجّل", guest_acc: "ضيف (لا تُحفَظ المحادثات)", theme: "لون الواجهة", dark: "أسود", light: "أبيض", language: "اللغة",
  pol: "سياسات الاستخدام",
  pols: ["لا مساعدة في صنع الأسلحة أو المتفجرات", "لا برمجيات خبيثة ولا اختراق حسابات الآخرين", "لا محتوى جنسي أو مخل بالآداب، وخصوصاً ما يتعلق بالقاصرين", "لا خطاب كراهية ولا تحريض ولا تهديد", "لا تعليمات لإيذاء النفس أو لأنشطة غير قانونية"],
  clear: "حذف كل المحادثات", cleared: "تم الحذف", close: "إغلاق",
  blocked: "عذراً، لا أستطيع المساعدة في هذا الطلب لأنه مخالف لسياسات الاستخدام.",
  expired: "انتهت الجلسة بسبب عدم النشاط", file: "الملف", sumfile: "لخّص الملف المرفق", due: "الموعد", otherlang: "English",
  topic_all: "كل المواضيع", gov: "🏛 مختبر الحوكمة", src: "المصادر", src_rel: "مصادر ذات صلة", copycode: "نسخ", copied_code: "تم"
},
en: {
  sub_login: "Sign in to continue", sub_reg: "Create your new account", email: "Email", pass: "Password (min. 8 characters)",
  login: "Sign in", register: "Create account", no_acc: "No account? Create one", has_acc: "Have an account? Sign in",
  guest: "Continue as guest", or: "or",
  sec: "🔒 Passwords are hashed on the server, and sessions expire after 30 minutes of inactivity",
  new: "New chat +", newchat: "New chat", hist: "Chat history", tasks: "Scheduled tasks", share: "Share", send: "Send",
  pause: "Pause ⏸", resume: "Resume ▶", cancel: "Cancel reply", ph: "Type your message in Arabic or English…",
  logout: "Log out", signin: "Sign in", guestname: "Guest", hello: "How can I help you today?",
  chips: ["Explain a concept", "What is the difference between TCP and UDP?", "كيف يعمل RAG؟"],
  e_email: "Enter a valid email address", e_pw: "Password needs 8+ characters with letters and numbers", e_exists: "This email is already registered",
  e_bad: "Incorrect email or password", e_lock: "Too many attempts. Try again in seconds: ", e_net: "Could not reach the server",
  e_rate: "Too many requests, wait a moment and try again", e_busy: "A reply is already being prepared, wait for it to finish",
  e_ollama: "Warning: Ollama is not running, replies will not work until you start it",
  pausedmsg: "⏸ The reply is being prepared in the background and will appear when ready…", ready: "Your reply is ready ✅", stopped: "Stopped.",
  failed: "Could not complete the reply.", notasks: "No scheduled tasks", t_ph: "What should the assistant do?", once: "Once", daily: "Every day",
  add: "Add task", t_bad: "Write the task and pick a future time", t_note: "Tasks run only while this page is open", t_ran: "A scheduled task ran ⏰",
  copy: "Copy", save: "Save as file", copied: "Chat copied", nothing: "Nothing to share yet", set: "Settings", acc: "Account info",
  member: "Registered user", guest_acc: "Guest (chats are not saved)", theme: "Interface color", dark: "Black", light: "White", language: "Language",
  pol: "Usage policies",
  pols: ["No help making weapons or explosives", "No malware or hacking other people’s accounts", "No sexual or indecent content, especially involving minors", "No hate speech, incitement or threats", "No instructions for self-harm or illegal activities"],
  clear: "Delete all chats", cleared: "Deleted", close: "Close",
  blocked: "Sorry, I can’t help with this request because it violates the usage policies.",
  expired: "Session expired due to inactivity", file: "File", sumfile: "Summarize the attached file", due: "Due", otherlang: "عربي",
  topic_all: "All topics", gov: "🏛 Governance Lab", src: "Sources", src_rel: "Related sources", copycode: "Copy", copied_code: "Done"
}};
const t = k => T[lang][k];

const BAD = [/how to (make|build|create) (a )?(bomb|explosive|nerve agent|bioweapon)/i, /child (porn|sexual)|csam/i,
  /write (me )?(a )?(ransomware|malware|keylogger|virus)/i, /hack (into )?(someone|a person|my (ex|neighbor))\S* ?(account|phone|wifi)?/i,
  /(طريقة|كيف).{0,12}(صنع|عمل|تصنيع).{0,10}(قنبلة|متفجرات|سلاح كيميائي|سلاح بيولوجي)/, /اباحي.{0,8}(اطفال|أطفال|للأطفال)/,
  /اكتب.{0,8}(فيروس|برنامج خبيث|برنامج فدية|كيلوقر)/, /اختراق (حساب|هاتف|واي ?فاي) (شخص|احد|أحد|جاري|طليق)/];
const blocked = s => BAD.some(r => r.test(s));

let chats = [], cur = null, tab = 1, att = null, user = null, mode = "login", tasks = [], tf = null, idle = null, topics = [];
const els = new WeakMap();
const ttl = c => c.title || t("newchat");
const isAr = s => /[\u0600-\u06FF]/.test(s);

function toast(m) {
  const d = document.createElement("div"); d.className = "toast"; d.textContent = m;
  document.body.appendChild(d); setTimeout(() => d.remove(), 2600);
}

/* ---------- server helpers ---------- */
async function api(path, method = "GET", body) {
  const r = await fetch(path, {
    method, credentials: "same-origin",
    headers: body !== undefined ? { "Content-Type": "application/json" } : {},
    body: body !== undefined ? JSON.stringify(body) : undefined
  });
  let data = {}; try { data = await r.json(); } catch (_) {}
  return { ok: r.ok, status: r.status, data };
}
const timers = {};
function persist(key, getter) {
  if (!user || user.guest) return;
  clearTimeout(timers[key]);
  timers[key] = setTimeout(() => api("/api/state/" + key, "PUT", { value: getter() })
    .then(r => { if (!r.ok) toast(r.status === 413 || (r.data && r.data.error === "too_large")
      ? (lang === "ar" ? "تعذّر حفظ المحادثات: الحجم كبير، احذف محادثات قديمة" : "Could not save chats: too large, delete old chats")
      : (lang === "ar" ? "تعذّر حفظ المحادثات" : "Could not save chats")); })
    .catch(() => toast(t("e_net"))), 700);
}
const chatsData = () => chats.map(c => ({
  id: c.id, title: c.title,
  msgs: c.msgs.filter(m => !m.pending).map(m => ({ role: m.role, content: m.content, file: m.file || null, sources: m.sources || [] }))
}));

/* ---------- UI texts ---------- */
function applyUI() {
  const r = document.documentElement; r.lang = lang; r.dir = lang === "ar" ? "rtl" : "ltr"; r.dataset.theme = theme;
  document.querySelectorAll("[data-i]").forEach(e => e.textContent = t(e.dataset.i));
  document.querySelectorAll("[data-p]").forEach(e => e.placeholder = t(e.dataset.p));
  $("alang").textContent = t("otherlang"); setMode(mode);
  $("out").textContent = user && user.guest ? t("signin") : t("logout");
  $("who").textContent = user ? (user.guest ? t("guestname") : user.email) : "";
  buildTF(); fillTopics(); if (user && cur) render();
}
function setLang(l) { lang = l; LS.set("lang", l); closeModal(); applyUI(); }
function setTheme(x) { theme = x; LS.set("theme", x); document.documentElement.dataset.theme = x; }
$("alang").onclick = () => setLang(lang === "ar" ? "en" : "ar");
$("atheme").onclick = () => setTheme(theme === "dark" ? "light" : "dark");

function fillTopics() {
  const sel = $("topic"), prev = sel.value || LS.get("topic") || "all";
  sel.innerHTML = "";
  const add = (v, label) => { const o = document.createElement("option"); o.value = v; o.textContent = label; sel.appendChild(o); };
  add("all", t("topic_all"));
  topics.forEach(tp => add(tp.id, lang === "ar" ? tp.ar : tp.en));
  sel.value = [...sel.options].some(o => o.value === prev) ? prev : "all";
}
$("topic").onchange = () => LS.set("topic", $("topic").value);

function sampleChips() {
  const pool = [];
  topics.forEach(tp => (tp.examples || []).forEach(e => { if (isAr(e) === (lang === "ar")) pool.push(e); }));
  if (pool.length < 3) return t("chips");
  for (let i = pool.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [pool[i], pool[j]] = [pool[j], pool[i]]; }
  return pool.slice(0, 3);
}

/* ---------- markdown (بدون innerHTML: كل شي عبر DOM) ---------- */
function inline(parent, s) {
  const re = /(`[^`\n]+`)|(\*\*[^*\n]+\*\*)|(\[[^\]\n]+\]\((https?:\/\/[^)\s]+)\))|(\[(\d+|A)\])/g;
  let last = 0, m;
  while ((m = re.exec(s))) {
    if (m.index > last) parent.append(s.slice(last, m.index));
    if (m[1]) { const c = document.createElement("code"); c.textContent = m[1].slice(1, -1); parent.append(c); }
    else if (m[2]) { const b = document.createElement("strong"); b.textContent = m[2].slice(2, -2); parent.append(b); }
    else if (m[3]) {
      const a = document.createElement("a"); a.textContent = m[3].slice(1, m[3].indexOf("]"));
      a.href = m[4]; a.target = "_blank"; a.rel = "noopener noreferrer"; parent.append(a);
    } else if (m[5]) { const sp = document.createElement("sup"); sp.className = "cite"; sp.textContent = m[5]; parent.append(sp); }
    last = re.lastIndex;
  }
  if (last < s.length) parent.append(s.slice(last));
}
function codeBlock(code) {
  const pre = document.createElement("pre"), c = document.createElement("code"); c.textContent = code; pre.append(c);
  const b = document.createElement("button"); b.className = "cpy"; b.textContent = t("copycode");
  b.onclick = async () => { try { await navigator.clipboard.writeText(code); b.textContent = t("copied_code"); setTimeout(() => b.textContent = t("copycode"), 1200); } catch (_) {} };
  pre.append(b); return pre;
}
const LI = /^\s*([-*•]|\d+[.)])\s+/, H = /^(#{1,4})\s+(.*)$/, HR = /^\s*---+\s*$/, FENCE = /^\s*```/;
function renderMd(el, text) {
  el.textContent = "";
  const lines = text.replace(/\r/g, "").split("\n"); let i = 0;
  while (i < lines.length) {
    const ln = lines[i];
    if (FENCE.test(ln)) {
      const code = []; i++;
      while (i < lines.length && !FENCE.test(lines[i])) { code.push(lines[i]); i++; }
      i++; el.append(codeBlock(code.join("\n"))); continue;
    }
    if (!ln.trim()) { i++; continue; }
    const h = ln.match(H);
    if (h) { const e = document.createElement("h" + Math.min(h[1].length + 2, 5)); e.dir = "auto"; inline(e, h[2]); el.append(e); i++; continue; }
    if (HR.test(ln)) { el.append(document.createElement("hr")); i++; continue; }
    if (LI.test(ln)) {
      const ord = /^\s*\d+[.)]/.test(ln), list = document.createElement(ord ? "ol" : "ul"); list.dir = "auto";
      while (i < lines.length && LI.test(lines[i])) {
        const li = document.createElement("li"); li.dir = "auto"; inline(li, lines[i].replace(LI, "")); list.append(li); i++;
      }
      el.append(list); continue;
    }
    const buf = [];
    while (i < lines.length && lines[i].trim() && !FENCE.test(lines[i]) && !H.test(lines[i]) && !LI.test(lines[i]) && !HR.test(lines[i])) { buf.push(lines[i]); i++; }
    const p = document.createElement("p"); p.dir = "auto";
    buf.forEach((b, k) => { if (k) p.append(document.createElement("br")); inline(p, b); });
    el.append(p);
  }
}
function srcBlock(m) {
  const d = document.createElement("div"); d.className = "src";
  const h = document.createElement("div"); h.className = "srch"; h.textContent = t(m.sources[0].related ? "src_rel" : "src"); d.append(h);
  m.sources.forEach(s => {
    const ok = s.url && /^https?:\/\//.test(s.url);
    const e = ok ? Object.assign(document.createElement("a"), { href: s.url, target: "_blank", rel: "noopener noreferrer" }) : document.createElement("span");
    e.textContent = s.title + (s.heading ? " — " + s.heading : ""); e.dir = "auto"; d.append(e);
  });
  return d;
}

/* ---------- chats ---------- */
function newChat() {
  if (cur && !cur.msgs.length) return render();
  cur = { id: Date.now() + Math.random(), title: "", msgs: [] }; chats.unshift(cur); render();
}
function render() {
  if (!cur) return;
  persist("chats", chatsData);
  $("title").textContent = ttl(cur);
  const l = $("list"); l.innerHTML = "";
  if (tab === 2) {
    l.appendChild(tf);
    if (!tasks.length) { const n = document.createElement("div"); n.className = "none"; n.textContent = t("notasks"); l.appendChild(n); }
    tasks.forEach(k => {
      const d = document.createElement("div"); d.className = "item"; const s = document.createElement("span");
      s.textContent = k.prompt + " · " + new Date(k.at).toLocaleString(lang === "ar" ? "ar-JO" : "en-US") + (k.repeat === "daily" ? " ↻" : "");
      const x = document.createElement("button"); x.textContent = "✕";
      x.onclick = () => { tasks = tasks.filter(z => z !== k); saveTasks(); render(); };
      d.append(s, x); l.appendChild(d);
    });
  } else chats.forEach(c => {
    const d = document.createElement("div"); d.className = "item" + (c === cur ? " on" : "");
    const s = document.createElement("span"); s.textContent = ttl(c);
    const x = document.createElement("button"); x.textContent = "✕";
    x.onclick = e => { e.stopPropagation(); if (c.ctrl) c.ctrl.abort(); chats = chats.filter(k => k !== c); if (c === cur) { cur = chats[0] || null; if (!cur) return newChat(); } render(); };
    d.onclick = () => { cur = c; c.unread = false; $("side").classList.remove("open"); render(); };
    if (c.unread) { const o = document.createElement("span"); o.className = "dot"; o.style.flex = "0"; o.textContent = "●"; d.append(o); }
    d.append(s, x); l.appendChild(d);
  });
  const box = $("msgs"); box.innerHTML = "";
  if (!cur.msgs.length) {
    const h = document.createElement("div"); h.className = "hello";
    h.innerHTML = '<div class="logo"><span>chat</span> <i>XVM</i></div><p></p>'; h.querySelector("p").textContent = t("hello");
    const c = document.createElement("div"); c.className = "chips";
    sampleChips().forEach(s => { const b = document.createElement("button"); b.textContent = s; b.dir = "auto"; b.onclick = () => { $("in").value = s; send(); }; c.appendChild(b); });
    h.appendChild(c); box.appendChild(h);
  } else { cur.msgs.forEach(m => box.appendChild(bubble(m))); box.scrollTop = box.scrollHeight; }
  const b = !!cur.busy;
  $("send").disabled = b; $("pause").disabled = !b; $("cancel").disabled = !b; $("pause").textContent = cur.paused ? t("resume") : t("pause");
  const fw = $("filewrap"); fw.innerHTML = "";
  if (att) { const f = document.createElement("button"); f.className = "file"; f.textContent = "📎 " + att.name + " ✕"; f.onclick = () => { att = null; render(); }; fw.appendChild(f); }
}
function fillBot(d, m) {
  if (m.pending && cur && cur.paused) { d.textContent = t("pausedmsg"); return; }
  if (m.pending && m.content === "…") { d.textContent = "…"; return; }
  renderMd(d, m.content);
  if (m.sources && m.sources.length) d.append(srcBlock(m));
}
function bubble(m) {
  const r = document.createElement("div"); r.className = "row " + (m.role === "user" ? "ur" : "br");
  const d = document.createElement("div"); d.className = "m " + (m.role === "user" ? "u" : "b md"); d.dir = "auto";
  if (m.role === "user") {
    if (m.file) { const f = document.createElement("div"); f.className = "fchip"; f.textContent = "📎 " + m.file; d.append(f, document.createElement("br")); }
    d.append(document.createTextNode(m.content));
  } else fillBot(d, m);
  if (m.pending) els.set(m, d);
  r.appendChild(d); return r;
}
let raf = null;
function liveUpdate(chat, reply) {
  if (raf) return;
  raf = requestAnimationFrame(() => {
    raf = null;
    const e = els.get(reply);
    if (e && chat === cur && !chat.paused) { fillBot(e, reply); const box = $("msgs"); box.scrollTop = box.scrollHeight; }
  });
}

/* ---------- asking the RAG server ---------- */
async function ask(chat, shown, attachment) {
  chat.msgs.push({ role: "user", content: shown, file: attachment ? attachment.name : null });
  if (!chat.title) chat.title = shown.slice(0, 28);
  if (blocked(shown)) { chat.msgs.push({ role: "assistant", content: t("blocked") }); return render(); }
  const reply = { role: "assistant", content: "…", pending: true, sources: [] };
  chat.msgs.push(reply); chat.busy = true; chat.paused = false; chat.ctrl = new AbortController(); render();
  const hist = chat.msgs.slice(0, -2).filter(m => !m.pending).slice(-6).map(m => ({ role: m.role, content: m.content }));
  let aborted = false, failed = null;
  try {
    const r = await fetch("/api/chat", {
      method: "POST", credentials: "same-origin", signal: chat.ctrl.signal, headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: shown, history: hist, topic: $("topic").value, attachment })
    });
    if (r.status === 401) { failed = "auth"; }
    else if (r.status === 429) { failed = t("e_rate"); }
    else if (r.status === 409) { failed = t("e_busy"); }
    else if (!r.ok || !r.body) { failed = t("failed"); }
    else {
      const rd = r.body.getReader(), dec = new TextDecoder(); let buf = "";
      for (;;) {
        const { value, done } = await rd.read(); if (done) break;
        buf += dec.decode(value, { stream: true });
        let i;
        while ((i = buf.indexOf("\n")) >= 0) {
          const line = buf.slice(0, i).trim(); buf = buf.slice(i + 1); if (!line) continue;
          let msg; try { msg = JSON.parse(line); } catch (_) { continue; }
          if (msg.t === "text") { reply.content = msg.v; liveUpdate(chat, reply); }
          else if (msg.t === "sources") { reply.sources = msg.v; }
          else if (msg.t === "error") { failed = msg.v === "internal_error" ? t("failed") : msg.v; }
        }
      }
    }
  } catch (e) {
    aborted = chat.ctrl.signal.aborted;
    if (!aborted) failed = t("e_net");
  }
  if (failed === "auth") { chat.msgs.pop(); chat.msgs.pop(); chat.busy = false; render(); showAuth(); toast(t("expired")); return; }
  if (aborted) reply.content = reply.content === "…" ? t("stopped") : reply.content;
  else if (failed) reply.content = (reply.content !== "…" ? reply.content + "\n\n" : "") + "⚠️ " + failed;
  else if (reply.content === "…") reply.content = t("failed");
  reply.pending = false; chat.busy = false;
  if (!aborted && !failed && (chat !== cur || chat.paused)) { toast(t("ready")); if (chat !== cur) chat.unread = true; }
  chat.paused = false; if (chats.includes(chat)) render();
}
function send() {
  const text = $("in").value.trim(); if ((!text && !att) || !cur || cur.busy) return;
  const shown = text || t("sumfile"), a = att ? { name: att.name, text: att.text.slice(0, 20000) } : null;
  $("in").value = ""; att = null; ask(cur, shown, a);
}
$("send").onclick = send;
$("pause").onclick = () => { if (cur && cur.busy) { cur.paused = !cur.paused; render(); } };
$("cancel").onclick = () => { if (cur && cur.ctrl) cur.ctrl.abort(); };
$("in").addEventListener("keydown", e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } });
$("in").dir = "auto";
$("new").onclick = () => { tab = 1; $("t1").className = "on"; $("t2").className = ""; $("side").classList.remove("open"); newChat(); };
$("t1").onclick = () => { tab = 1; $("t1").className = "on"; $("t2").className = ""; render(); };
$("t2").onclick = () => { tab = 2; $("t2").className = "on"; $("t1").className = ""; render(); };
$("clip").onclick = () => $("fi").click();
$("fi").onchange = async e => { const f = e.target.files[0]; if (!f) return; att = { name: f.name, text: await f.text() }; e.target.value = ""; render(); };
$("menu").onclick = () => $("side").classList.add("open");
$("closeside").onclick = () => $("side").classList.remove("open");

/* ---------- scheduled tasks (تنفّذ والصفحة مفتوحة) ---------- */
function saveTasks() { persist("tasks", () => tasks); }
function buildTF() {
  tf = document.createElement("div"); tf.className = "tf";
  const p = document.createElement("textarea"); p.rows = 2; p.placeholder = t("t_ph"); p.dir = "auto";
  const w = document.createElement("input"); w.type = "datetime-local";
  const r = document.createElement("select");
  [["once", "once"], ["daily", "daily"]].forEach(([v, k]) => { const o = document.createElement("option"); o.value = v; o.textContent = t(k); r.appendChild(o); });
  const b = document.createElement("button"); b.className = "newbtn"; b.textContent = t("add");
  const n = document.createElement("small"); n.textContent = t("t_note");
  b.onclick = () => {
    const at = new Date(w.value).getTime();
    if (!p.value.trim() || !at || at <= Date.now()) return toast(t("t_bad"));
    tasks.push({ id: Date.now(), prompt: p.value.trim(), at, repeat: r.value }); saveTasks(); p.value = ""; w.value = ""; render();
  };
  tf.append(p, w, r, b, n);
}
function runTask(k) {
  const c = { id: Date.now() + Math.random(), title: "⏰ " + k.prompt.slice(0, 24), msgs: [] };
  chats.unshift(c); toast(t("t_ran")); ask(c, k.prompt, null);
}
setInterval(() => {
  if (!user || !tasks.length) return; const now = Date.now(); let ch = false;
  tasks.slice().forEach(k => {
    if (k.at <= now) {
      ch = true; runTask(k);
      if (k.repeat === "daily") { while (k.at <= now) k.at += 864e5; } else tasks = tasks.filter(z => z !== k);
    }
  });
  if (ch) { saveTasks(); render(); }
}, 15000);

/* ---------- modals: share + settings ---------- */
function openModal(build) {
  const c = $("mcard"); c.innerHTML = ""; build(c);
  const x = document.createElement("button"); x.className = "guest"; x.textContent = t("close"); x.onclick = closeModal; c.appendChild(x);
  $("modal").hidden = false;
}
function closeModal() { $("modal").hidden = true; }
$("modal").onclick = e => { if (e.target.id === "modal") closeModal(); };
$("share").onclick = () => {
  const txt = cur ? cur.msgs.filter(m => !m.pending).map(m => (m.role === "user" ? (lang === "ar" ? "أنا: " : "Me: ") : "chat XVM: ") + m.content).join("\n\n") : "";
  if (!txt) return toast(t("nothing"));
  openModal(c => {
    const h = document.createElement("h3"); h.textContent = t("share");
    const a = document.createElement("textarea"); a.readOnly = true; a.value = txt; a.dir = "auto";
    const cp = document.createElement("button"); cp.className = "newbtn"; cp.textContent = t("copy");
    cp.onclick = async () => { try { await navigator.clipboard.writeText(txt); toast(t("copied")); } catch (_) { a.select(); toast(t("copied")); } };
    const s = document.createElement("button"); s.className = "guest"; s.textContent = t("save");
    s.onclick = () => {
      const url = URL.createObjectURL(new Blob([txt], { type: "text/plain;charset=utf-8" }));
      const l = document.createElement("a"); l.href = url; l.download = "chat-xvm.txt"; document.body.appendChild(l); l.click(); l.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
    };
    c.append(h, a, cp, s);
  });
};
function openSettings() {
  openModal(c => {
    const mk = (tag, txt) => { const e = document.createElement(tag); e.textContent = txt; return e; };
    const seg = (items, val, fn) => { const s = document.createElement("div"); s.className = "seg"; items.forEach(([v, l]) => { const b = mk("button", l); if (v === val) b.className = "on"; b.onclick = () => fn(v); s.appendChild(b); }); return s; };
    c.append(mk("h3", "⚙ " + t("set")), mk("h4", t("acc")), mk("div", user.guest ? t("guest_acc") : t("member") + " · " + user.email),
      mk("h4", t("theme")), seg([["dark", t("dark")], ["light", t("light")]], theme, v => { setTheme(v); openSettings(); }),
      mk("h4", t("language")), seg([["ar", "العربية"], ["en", "English"]], lang, setLang),
      mk("h4", t("pol")));
    const u = document.createElement("ul"); t("pols").forEach(p => u.appendChild(mk("li", p))); c.appendChild(u);
    const d = mk("button", t("clear")); d.className = "guest";
    d.onclick = () => { chats.forEach(k => k.ctrl && k.ctrl.abort()); chats = []; cur = null; newChat(); toast(t("cleared")); closeModal(); };
    c.appendChild(d);
  });
}
$("gear").onclick = openSettings; $("gear2").onclick = openSettings;

/* ---------- auth (الخادم هو اللي بيتحقق ويحفظ) ---------- */
async function loadTopics() {
  try { const r = await api("/api/topics"); topics = r.data.topics || []; } catch (_) { topics = []; }
}
async function start(u) {
  user = u; chats = []; tasks = []; cur = null;
  if (!u.guest) {
    try {
      const [a, b] = await Promise.all([api("/api/state/chats"), api("/api/state/tasks")]);
      chats = (a.data.value || []).map(c => ({ ...c, msgs: c.msgs || [] })); tasks = b.data.value || [];
    } catch (_) {}
  }
  await loadTopics();
  cur = chats[0] || null; $("auth").hidden = true; applyUI(); if (!cur) newChat(); touch();
  try { const h = await api("/api/health"); if (!h.data.ollama) toast(t("e_ollama")); } catch (_) {}
}
function showAuth() {
  user = null; chats = []; tasks = []; cur = null; $("auth").hidden = false; $("pw").value = ""; $("err").textContent = ""; applyUI();
}
function setMode(m) {
  mode = m; const l = m === "login";
  $("go").textContent = t(l ? "login" : "register"); $("asub").textContent = t(l ? "sub_login" : "sub_reg");
  $("sw").textContent = t(l ? "no_acc" : "has_acc"); $("err").textContent = ""; $("pw").autocomplete = l ? "current-password" : "new-password";
}
$("sw").onclick = () => setMode(mode === "login" ? "register" : "login");
function authError(r) {
  const c = r.data && r.data.error;
  if (c === "locked") return t("e_lock") + (r.data.retry || 60);
  if (c === "exists") return t("e_exists");
  if (c === "weak_password") return t("e_pw");
  if (c === "bad_email") return t("e_email");
  if (c === "bad_credentials") return t("e_bad");
  return t("e_net");
}
$("go").onclick = async () => {
  const email = $("em").value.trim().toLowerCase(), pw = $("pw").value, err = $("err");
  if (!/^\S+@\S+\.\S+$/.test(email)) return err.textContent = t("e_email");
  if (mode === "register" && (pw.length < 8 || !/[A-Za-z\u0600-\u06FF]/.test(pw) || !/\d/.test(pw))) return err.textContent = t("e_pw");
  $("go").disabled = true;
  try {
    const r = await api(mode === "login" ? "/api/login" : "/api/register", "POST", { email, password: pw });
    if (r.ok) await start({ email: r.data.email }); else err.textContent = authError(r);
  } catch (_) { err.textContent = t("e_net"); }
  $("go").disabled = false;
};
$("pw").addEventListener("keydown", e => { if (e.key === "Enter") $("go").click(); });
$("em").addEventListener("keydown", e => { if (e.key === "Enter") $("pw").focus(); });
$("gu").onclick = async () => {
  try { const r = await api("/api/guest", "POST", {}); if (r.ok) await start({ guest: true }); else $("err").textContent = t("e_net"); }
  catch (_) { $("err").textContent = t("e_net"); }
};
async function logout(msg) {
  chats.forEach(k => k.ctrl && k.ctrl.abort());
  try { await api("/api/logout", "POST", {}); } catch (_) {}
  showAuth(); if (msg) toast(msg);
}
$("out").onclick = () => logout();
function touch() { clearTimeout(idle); if (user && !user.guest) idle = setTimeout(() => logout(t("expired")), 18e5); }
["click", "keydown"].forEach(ev => addEventListener(ev, touch));

/* ---------- init ---------- */
applyUI();
(async () => {
  try {
    const r = await api("/api/me");
    if (r.ok) await start(r.data.guest ? { guest: true } : { email: r.data.email });
  } catch (_) {}
})();
