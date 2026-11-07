"""الواجهة:  python app.py   (لازم Ollama شغال)"""
import re
import gradio as gr, yaml
from rag import answer_stream

TOPICS = yaml.safe_load(open("topics.yaml", encoding="utf-8"))
CHOICES = [("كل المواضيع / All topics", "all")] + [(f"{v['ar']} / {v['en']}", k) for k, v in TOPICS.items()]


def as_text(content):
    """Gradio الجديد ممكن يرجع المحتوى كنص أو كقائمة كتل؛ نحوله لنص عادي."""
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        return as_text(content.get("text") or content.get("content") or "")
    if isinstance(content, (list, tuple)):
        return " ".join(as_text(c) for c in content)
    return str(content or "")


def clean_history(history):
    out = []
    for h in history or []:
        if isinstance(h, dict):
            out.append({"role": h.get("role", "user"), "content": as_text(h.get("content"))})
    return out


def fmt_sources(metas, text=""):
    cited = {int(n) for n in re.findall(r"\[(\d+)\]", text)}
    chosen = [m for i, m in enumerate(metas, 1) if i in cited]
    label = "المصادر / Sources"
    if not chosen and metas:                       # النموذج ما استشهد: نعرض أقرب مصدرين بتسمية صريحة
        chosen = metas[:2]
        label = "مصادر ذات صلة (غير مستشهد بها مباشرة) / Related sources"
    seen, lines = set(), []
    for m in chosen:
        key = (m["page_url"], m["heading"])
        if key in seen:
            continue
        seen.add(key)
        title = f"{m['source_title']} — {m['heading']}"
        lines.append(f"- [{title}]({m['page_url']})" if m["page_url"].startswith("http") else f"- {title}")
    return f"\n\n---\n**{label}**\n" + "\n".join(lines) if lines else ""


def chat(message, history, topic):
    message = as_text(message)
    last, srcs = "", []
    try:
        for text, srcs in answer_stream(message, clean_history(history), topic):
            last = text
            yield text
    except Exception as e:      # أخطاء Ollama أو الفهرس بتظهر بالواجهة بدل ما تكسرها
        yield f"⚠️ خطأ: {e}\n\nتأكد أن Ollama شغال وأنك شغّلت build_index.py"
        return
    yield last + fmt_sources(srcs, last)


examples = [[ex, k] for k, v in TOPICS.items() for ex in v["examples"][:1]]

# ---- اتجاه النص: كل فقرة بتتجه حسب لغتها (عربي = من اليمين لليسار، إنجليزي = من اليسار لليمين) ----
CSS = """
[dir="auto"] { text-align: start !important; }
pre, code { direction: ltr !important; text-align: left !important; unicode-bidi: isolate; }
ul[dir="auto"], ol[dir="auto"] { padding-inline-start: 1.6em; padding-inline-end: 0; }
"""

JS = """
() => {
  const SEL = 'p, li, ul, ol, h1, h2, h3, h4, h5, h6, blockquote, td, th, textarea, input[type="text"]';
  const mark = (el) => { if (el.nodeType === 1 && !el.hasAttribute('dir')) el.setAttribute('dir', 'auto'); };
  const apply = (root) => {
    if (!root || root.nodeType !== 1) return;
    if (root.matches && root.matches(SEL)) mark(root);
    if (root.querySelectorAll) root.querySelectorAll(SEL).forEach(mark);
  };
  apply(document.body);
  new MutationObserver((muts) => muts.forEach((m) => m.addedNodes.forEach(apply)))
    .observe(document.body, { childList: true, subtree: true });
}
"""

# Gradio 6 نقل css و js من Blocks إلى launch()، و Gradio 5 بياخدهم بالـ constructor
import inspect
LAUNCH_TAKES_CSS = "css" in inspect.signature(gr.Blocks.launch).parameters


def build():
    kwargs = dict(
        additional_inputs=[gr.Dropdown(CHOICES, value="all", label="الموضوع / Topic")],
        examples=examples,
        title="TechTutor — مدرّس التقنية",
        description="اسأل بالعربي أو بالإنجليزي عن البرمجة، الذكاء الاصطناعي، الشبكات، الروبوتات وغيرها.",
    )
    if not LAUNCH_TAKES_CSS:
        kwargs.update(css=CSS, js=JS)
    return gr.ChatInterface(chat, **kwargs)


demo = build()

if __name__ == "__main__":
    if LAUNCH_TAKES_CSS:
        demo.launch(css=CSS, js=JS)
    else:
        demo.launch()
