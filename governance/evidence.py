"""بوابة الأدلة (Evidence gate): أي اقتباس بيستشهد فيه وكيل لازم يكون موجود بالمقطع اللي انعرض عليه، وبنفس المعنى.

قواعد التحقق:
  1. بعد التطبيع (حركات، أشكال الألف/الياء، علامات ترقيم) الاقتباس موجود حرفياً بالمقطع => score 1.0
  2. وإلا: تطابق تقريبي (لفروقات استخراج PDF) بشرط إنه الجزء المقابل بالمصدر ما فيه كلام منقوص أو زيادة،
     وما في أي رقم مختلف، وما في نفي/استثناء موجود بطرف ومش بالثاني (لا/غير/without/not ...).
  3. السجل بيخزّن نص المصدر الفعلي (source_span) مش صياغة الوكيل.
الاقتباس المرفوض بيتسجل، والقرار بلا دليل موثّق بيتحوّل لـ NEED_INFO (تصعيد لإنسان).
"""
import math
import re
import unicodedata
from difflib import SequenceMatcher

_AR_DIACRITICS = re.compile(r"[ؐ-ًؚ-ٰٟۖ-ۭـ]")
_PUNCT = re.compile(r"[^\w\s]", re.UNICODE)
_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")


def normalize(text):
    t = unicodedata.normalize("NFKC", str(text or "")).lower().translate(_DIGITS)
    t = _AR_DIACRITICS.sub("", t)
    t = (t.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ٱ", "ا")
          .replace("ى", "ي").replace("ی", "ي").replace("ک", "ك").replace("ة", "ه").replace("ؤ", "و").replace("ئ", "ي"))
    t = t.replace("’", "'").replace("“", '"').replace("”", '"')
    t = re.sub(r"(?<=\d)[,.](?=\d{3}\b)", "", t)          # 2,000 = 2000
    t = _PUNCT.sub(" ", t)
    return re.sub(r"\s+", " ", t).strip()


MIN_QUOTE_WORDS = 5           # أقل طول لأي اقتباس
MIN_DECISIVE_WORDS = 8        # أقل طول لاقتباس بيبني عليه قرار إيقاف أو شروط
FUZZY_MIN = 0.92              # للتسامح مع فروقات بسيطة ناتجة عن استخراج النص من PDF
_NEG = {"not", "no", "without", "except", "unless", "never", "nor", "cannot", "لا", "غير", "ليس", "دون", "الا", "عدم", "بدون", "لن", "لم"}


def _words(t):
    return t.split()


def _meaning_changed(q_words, s_words):
    """رقم مختلف أو نفي/استثناء موجود بطرف واحد = المعنى تغيّر."""
    qn = {w for w in q_words if re.fullmatch(r"\d+", w)}
    sn = {w for w in s_words if re.fullmatch(r"\d+", w)}
    if qn != sn:
        return True
    return bool(({w for w in q_words if w in _NEG}) ^ ({w for w in s_words if w in _NEG}))


def match_quote(quote, source_text):
    """بيرجع (درجة 0..1، النص المقابل من المصدر). 1 = موجود حرفياً بعد التطبيع."""
    q, s = normalize(quote), normalize(source_text)
    if not q or len(q.split()) < MIN_QUOTE_WORDS:
        return 0.0, ""
    if q in s:
        # اقتباس حرفي بس قاطع النفي اللي قبله ("لا يجوز ..." صار "يجوز ...") = معنى معكوس
        i = s.find(q)
        before = s[:i].split()[-2:]
        if any(w in _NEG for w in before) and not any(w in _NEG for w in q.split()[:2]):
            return 0.5, " ".join(before + [q])
        return 1.0, q
    sm = SequenceMatcher(None, s, q, autojunk=False)
    blocks = [b for b in sm.get_matching_blocks() if b.size >= 4]
    if not blocks:
        return 0.0, ""
    covered = sum(b.size for b in blocks)
    if covered / len(q) < FUZZY_MIN:
        return covered / len(q), ""
    start, end = blocks[0].a, blocks[-1].a + blocks[-1].size
    # وسّع للحدود الكاملة للكلمات بالمصدر
    while start > 0 and s[start - 1] != " ":
        start -= 1
    while end < len(s) and s[end] != " ":
        end += 1
    span = s[start:end].strip()
    # كلام منقوص من المصدر (مثلاً "لا" أو "72" صارت "7") أو مضاف: مرفوض
    if abs(len(span) - len(q)) > max(6, 0.05 * len(q)):
        return 0.5, span
    if _meaning_changed(_words(q), _words(span)):
        return 0.5, span
    return covered / len(q), span


def _original_span(norm_span, source_text):
    """النص الأصلي (قبل التطبيع) المقابل: بندوّر على أول وآخر كلمة."""
    words = norm_span.split()
    if not words:
        return ""
    src_words = source_text.split()
    norm_src = [normalize(w) for w in src_words]
    n = len(words)
    for i in range(len(norm_src)):
        if norm_src[i] == words[0]:
            j = min(len(src_words), i + n + 3)
            for k in range(i + 1, j + 1):
                if normalize(" ".join(src_words[i:k])) == norm_span:
                    return " ".join(src_words[i:k])
    return norm_span


def verify_citations(citations, hits, visible_chars=None):
    """citations: [{"ref": رقم المقطع (1-based), "quote": "..."}]  hits: المقاطع اللي انعرضت على الوكيل.
    visible_chars: إذا المقطع انقص بالعرض، بنتحقق بس من الجزء اللي شافه الوكيل.
    بيرجع (verified, rejected). كل عنصر موثّق فيه source_span و doc_id/title/page/url للسجل."""
    verified, rejected = [], []
    for c in citations or []:
        if not isinstance(c, dict):
            continue
        quote = str(c.get("quote", "")).strip()
        try:
            ref = int(str(c.get("ref", "")).strip("[] UuBb"))
        except ValueError:
            ref = None
        order = list(range(len(hits)))
        if ref and 1 <= ref <= len(hits):
            order.remove(ref - 1)
            order.insert(0, ref - 1)
        best, best_i, best_span = 0.0, None, ""
        for i in order:
            text = hits[i]["text"][:visible_chars] if visible_chars else hits[i]["text"]
            score, span = match_quote(quote, text)
            if score > best:
                best, best_i, best_span = score, i, span
            if score >= 1.0:
                break
        if best >= FUZZY_MIN and best_i is not None:
            h = hits[best_i]
            m = h["meta"]
            text = h["text"][:visible_chars] if visible_chars else h["text"]
            exact = normalize(quote) in normalize(text)
            verified.append({"quote": quote, "source_span": quote if exact else _original_span(best_span, text),
                             "score": round(best, 3), "words": len(normalize(quote).split()), "chunk_id": h["id"],
                             "doc_id": m.get("doc_id"), "title": m.get("title"), "issuer": m.get("issuer"),
                             "category": m.get("category"), "binding_scope": m.get("binding_scope", ""),
                             "page": m.get("page"), "article": m.get("article"), "url": m.get("url"), "ref_given": ref,
                             "ref_corrected": ref is None or best_i + 1 != ref})
            art = _quote_article(quote)
            if art and art != str(m.get("article") or ""):
                verified[-1]["article_chunk"], verified[-1]["article"] = m.get("article"), art
        else:
            words = len(normalize(quote).split())
            reason = ("too_short" if words < MIN_QUOTE_WORDS else
                      "meaning_changed" if best == 0.5 else "not_found_verbatim")
            rejected.append({"quote": quote[:400], "ref_given": ref, "best_score": round(best, 3), "reason": reason})
    return verified, rejected


def _cos(a, b):
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(x * x for x in b))
    return sum(x * y for x, y in zip(a, b)) / (na * nb) if na and nb else 0.0


def score_relevance(verified, issue_text):
    """تشابه (cosine) بين كل اقتباس موثّق ونص المشكلة الحالية. الاقتباس ممكن يكون حقيقي بس مش ذو صلة.
    إذا التضمين فشل: relevance=None و relevance_error=True (وبيُعامل كغير ذي صلة بقرار الإيقاف)."""
    if not verified or not issue_text:
        return verified
    try:
        from . import retrieval
        vecs = retrieval.embed_many([issue_text[:1500]] + [c.get("source_span") or c["quote"] for c in verified])
    except Exception:
        for c in verified:
            c["relevance"], c["relevance_error"] = None, True
        return verified
    for c, v in zip(verified, vecs[1:]):
        c["relevance"] = round(_cos(vecs[0], v), 3)
    return verified


def _quote_article(quote):
    """إذا الاقتباس بيبلش بعنوان مادة ("Article (12) ..." / "المادة (12) ...") بنعتمد رقمها بدل أول مادة بالمقطع."""
    try:
        from .itu_ingest import _ARTICLE_HEAD, _art_value
    except Exception:
        return None
    m = _ARTICLE_HEAD.match(str(quote).strip())
    return _art_value(m) if m else None


def is_relevant(c, threshold):
    return c.get("relevance") is not None and c["relevance"] >= threshold


def decisive(c, threshold):
    """اقتباس بيصلح يكون أساس لقرار ملزم: طويل كفاية، ذو صلة، ومن نص إماراتي ملزم (مش منطقة حرة ولا مرجع دولي)."""
    return (c.get("words", 0) >= MIN_DECISIVE_WORDS and is_relevant(c, threshold)
            and c.get("binding_scope", "") in ("federal", "emirate"))
