"""إعدادات طبقة الحوكمة (Governance Sandbox) — كلها قابلة للتغيير بمتغيرات البيئة."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KB_DIR = ROOT / "knowledge_base"
POLICY_DIR = KB_DIR / "policy_docs"            # وثائق السياسات مقسمة لمجلدات = فئات (نفس فكرة InputDocs عند ITU)
POLICY_MANIFEST = POLICY_DIR / "manifest.yaml"
FRAMEWORK_JSON = KB_DIR / "framework" / "itu_ai_readiness_dimensions.json"
CHROMA_DIR = KB_DIR / "chroma"
POLICY_EXPORT = KB_DIR / "policy_kb_export.jsonl"   # نسخة مفتوحة من قاعدة المعرفة للتسليم
SCENARIO_DIR = ROOT / "scenarios"
AUDIT_DIR = ROOT / "data" / "audit"
REPORT_DIR = ROOT / "reports"

POLICY_COLLECTION = os.getenv("POLICY_COLLECTION", "kb_policy_uae")
FRAMEWORK_COLLECTION = os.getenv("FRAMEWORK_COLLECTION", "kb_framework")

OLLAMA = os.getenv("OLLAMA_HOST", "http://localhost:11434")
# bge-m3 لأنه بيدعم العربي. للتطابق الحرفي مع كود ITU المرجعي: EMBED_MODEL=nomic-embed-text
EMBED_MODEL = os.getenv("EMBED_MODEL", "bge-m3")

# مزوّد نموذج التوليد: ollama (افتراضي، محلي بالكامل) أو gemini (اختياري)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()
CHAT_MODEL = os.getenv("CHAT_MODEL", "qwen2.5:7b")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
LLM_FALLBACK = os.getenv("LLM_FALLBACK", "1") == "1"     # إذا Gemini فشل نرجع لـ Ollama
AGENT_MAX_TOKENS = int(os.getenv("AGENT_MAX_TOKENS", "500"))   # أقل = أسرع على المعالج
MAX_QUESTIONS = int(os.getenv("MAX_QUESTIONS", "1"))             # أسئلة لكل وكيل بالمرحلة (كل سؤال = رد إضافي)
PASSAGE_CHARS = int(os.getenv("PASSAGE_CHARS", "900"))           # طول كل مقطع بالـ prompt
GAP_ABSENCE_SIM = float(os.getenv("GAP_ABSENCE_SIM", "0.5"))     # فجوة "missing" بس في نص إماراتي قريب => للمراجعة
EVIDENCE_REL_MIN = float(os.getenv("EVIDENCE_REL_MIN", "0.45"))  # أقل تشابه بين الاقتباس والمشكلة ليعتبر دليل على BLOCK

POLICY_TOP_K = int(os.getenv("POLICY_TOP_K", "5"))
POLICY_MAX_DIST = float(os.getenv("POLICY_MAX_DIST", "0.62"))

GPU_OPT = {"num_gpu": int(os.environ["OLLAMA_NUM_GPU"])} if os.getenv("OLLAMA_NUM_GPU") not in (None, "") else {}

CATEGORIES = ["UAE_Education", "UAE_Data_Protection", "UAE_AI_Governance", "International_Benchmarks", "ITU_Standards"]
UAE_CATEGORIES = ["UAE_Education", "UAE_Data_Protection", "UAE_AI_Governance"]
