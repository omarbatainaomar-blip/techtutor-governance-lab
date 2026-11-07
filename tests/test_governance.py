"""اختبارات بدون Ollama ولا Chroma (بنستبدلهم بنسخ وهمية).  python -m unittest discover tests"""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from governance import audit, config as C, coordinator, evidence, llm, retrieval, scenarios
from governance.itu_ingest import chunk_text, _article_in

PDPL = ("Article (4) Consent. The Controller may not process Personal Data without the consent of the Data Subject, "
        "and consent of the guardian is required where the Data Subject is a child or lacks full legal capacity.")
XFER = ("Article (22) Cross-Border Transfer. Personal Data may be transferred outside the State only to countries "
        "with an adequate level of protection approved by the Data Office.")
UNESCO = ("Governments should set an age limit of 13 for the independent use of generative AI tools in the classroom "
          "and require validation of AI tools before use by schools.")


def hit(i, text, cat, title, scope=None):
    scope = scope or ("federal" if cat.startswith("UAE") else "international")
    return {"id": f"doc{i}:1:{i}", "text": text, "dist": 0.3,
            "meta": {"doc_id": f"doc{i}", "title": title, "category": cat, "page": 1, "article": "", "issuer": "x",
                     "binding_scope": scope}}


HITS = [hit(1, PDPL, "UAE_Data_Protection", "PDPL"), hit(2, XFER, "UAE_Data_Protection", "PDPL"),
        hit(3, UNESCO, "International_Benchmarks", "UNESCO GenAI guidance")]


def fake_search_policy(query, categories=None, k=None, max_dist=None):
    return [h for h in HITS if not categories or h["meta"]["category"] in categories]


def fake_chat(messages, json_mode=False, temperature=0.1, max_tokens=None):
    sys_ = messages[0]["content"]
    if "GAP ANALYSIS" in sys_:
        out = {"gaps": [{"title": "No explicit age limit for GenAI in UAE federal texts", "description": "d",
                         "uae_status": "missing", "uae_citations": [],
                         "benchmark_citations": [{"ref": "B1", "quote": "set an age limit of 13 for the independent use of generative AI tools"}],
                         "recommendation": "r", "y3172_node": "P", "readiness_dimension": "Governance"}]}
    elif '"data_office"' in sys_:
        out = {"assessment": "Guardian consent missing.", "verdict": "BLOCK", "risk": "high", "conditions": [],
               "citations": [{"ref": 2, "quote": "consent of the guardian is required where the Data Subject is a child"}],
               "questions": [{"to": "tutor", "question": "Can you delete stored IDs?"}], "rationale": ["a", "b"]}
    elif '"moe"' in sys_:   # يدّعي اقتباس غير موجود -> لازم ينرفض وينزل قراره
        out = {"assessment": "x", "verdict": "CONDITIONS", "risk": "medium", "conditions": ["teacher oversight"],
               "citations": [{"ref": 1, "quote": "schools must always obtain ministry approval for every AI tool"}]}
    else:
        out = {"assessment": "ok", "verdict": "APPROVE", "risk": "low", "conditions": ["minimise logs"], "citations": []}
    return json.dumps(out), {"provider": "fake", "model": "fake"}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self._orig = (retrieval.search_policy, retrieval.search_framework, retrieval.stats, llm.chat, C.AUDIT_DIR,
                      retrieval.embed_many)
        retrieval.embed_many = lambda texts, batch=16: [[1.0, 0.0]] * len(texts)      # كل الاقتباسات ذات صلة
        retrieval.search_policy = fake_search_policy
        retrieval.search_framework = lambda q, k=3: []
        retrieval.stats = lambda: {"kb_policy_uae": 3}
        llm.chat = fake_chat
        C.AUDIT_DIR = self.tmp

    def tearDown(self):
        (retrieval.search_policy, retrieval.search_framework, retrieval.stats, llm.chat, C.AUDIT_DIR,
         retrieval.embed_many) = self._orig
        shutil.rmtree(self.tmp, ignore_errors=True)


class TestEvidence(unittest.TestCase):
    def test_verbatim_and_wrong_ref(self):
        v, r = evidence.verify_citations([{"ref": 3, "quote": "consent of the guardian is required where the Data Subject"}], HITS)
        self.assertEqual(len(v), 1)
        self.assertTrue(v[0]["ref_corrected"])

    def test_invented_quote_rejected(self):
        v, r = evidence.verify_citations([{"ref": 1, "quote": "all schools must register every AI tool with the ministry"}], HITS)
        self.assertEqual(v, [])
        self.assertEqual(r[0]["reason"], "not_found_verbatim")

    def test_meaning_change_rejected(self):
        src = "The Controller may not process Personal Data without the consent of the Data Subject in any case."
        self.assertLess(evidence.match_quote("The Controller may process Personal Data without the consent of the Data Subject", src)[0], 0.9)
        src2 = "Data breaches must be reported to the Data Office within 72 hours of becoming aware of them."
        self.assertLess(evidence.match_quote("Data breaches must be reported to the Data Office within 7 hours of becoming aware", src2)[0], 0.9)

    def test_arabic_normalization(self):
        src = "لا يجوز للمتحكم معالجة البيانات الشخصية دون موافقة صاحب البيانات."
        self.assertEqual(evidence.match_quote("لا يجوز للمتحكم معالجة البيانات الشخصيّة دون موافقة", src)[0], 1.0)


class TestAudit(unittest.TestCase):
    def test_chain_detects_tampering(self):
        d = Path(tempfile.mkdtemp())
        orig, C.AUDIT_DIR = C.AUDIT_DIR, d
        self.addCleanup(setattr, C, "AUDIT_DIR", orig)
        log = audit.AuditLog("t", directory=d)
        log.log("run_start", "coordinator", {})
        for i in range(3):
            log.log("x", "a", {"i": i})
        recs = audit.read_log(log.path)
        self.assertEqual(audit.verify_chain(recs), (True, None))
        recs[1]["payload"]["i"] = 99
        self.assertEqual(audit.verify_chain(recs), (False, 2))
        shutil.rmtree(d)

    def test_truncation_detected_by_index(self):
        d = Path(tempfile.mkdtemp())
        orig, C.AUDIT_DIR = C.AUDIT_DIR, d
        self.addCleanup(setattr, C, "AUDIT_DIR", orig)
        log = audit.AuditLog("t2", directory=d)
        log.log("run_start", "coordinator", {})
        for i in range(3):
            log.log("x", "a", {"i": i})
        log.close()
        recs = audit.read_log(log.path)
        self.assertEqual(audit.verify_chain(recs), (True, None))
        self.assertFalse(audit.verify_chain(recs[:-1])[0])       # حذف آخر حدث بيبين من الفهرس
        shutil.rmtree(d)


class TestDecide(unittest.TestCase):
    GOOD = {"words": 12, "relevance": 0.8, "binding_scope": "federal"}

    def test_rules(self):
        auth = lambda v, cv=True, flags=(), a="x": {"agent": a, "verdict": v, "_authority": True,
                                                     "citations_verified": [dict(self.GOOD)] if cv else [], "flags": list(flags)}
        self.assertEqual(coordinator.decide([auth("BLOCK")])["status"], "SUSPEND")
        # إيقاف بدليل من منطقة حرة أو مرجع دولي ما بيكفي لـ SUSPEND
        fz = auth("BLOCK"); fz["citations_verified"][0]["binding_scope"] = "free_zone"
        self.assertNotEqual(coordinator.decide([fz])["status"], "SUSPEND")
        # أشد قرار بالمرحلة بيضل: BLOCK بالجولة الأولى ما بيمحيه APPROVE بالجولة الثانية
        self.assertEqual(coordinator.decide([auth("BLOCK", a="y"), auth("APPROVE", a="y")])["status"], "SUSPEND")
        self.assertEqual(coordinator.decide([auth("NEED_INFO", False)])["status"], "ESCALATE_TO_HUMAN")
        self.assertEqual(coordinator.decide([auth("CONDITIONS"), auth("APPROVE")])["status"], "CONTINUE_WITH_CONDITIONS")
        self.assertEqual(coordinator.decide([auth("APPROVE")])["status"], "CONTINUE")
        self.assertEqual(coordinator.decide([], "SUSPEND")["status"], "SUSPEND")


class TestRun(Base):
    def test_full_scenario(self):
        sc = scenarios.load("s1_student_data_offshore")
        co = coordinator.Coordinator(sc)
        co.run()
        recs = audit.read_log(co.log.path)
        self.assertTrue(audit.verify_chain(recs)[0])
        types = [r["type"] for r in recs]
        self.assertEqual(types[0], "run_start")
        self.assertEqual(types[-1], "run_end")
        self.assertEqual(types.count("decision"), len(sc["stages"]))
        moe = [r["payload"] for r in recs if r["type"] == "agent_response" and r["actor"] == "moe"]
        self.assertTrue(all(m["verdict"] == "NEED_INFO" and "unsupported_verdict" in m["flags"] for m in moe))
        dec = [r["payload"]["status"] for r in recs if r["type"] == "decision"]
        self.assertIn("SUSPEND", dec)
        msgs = [r for r in recs if r["type"] == "message"]
        self.assertTrue(msgs and msgs[0]["payload"]["recipient"] == "tutor")
        gaps = next(r for r in recs if r["type"] == "gap_analysis")["payload"]["gaps"]
        self.assertEqual(gaps[0]["evidence_level"], "benchmark")
        from governance import report
        self.assertIn("Policy gap analysis", report.render(recs))

    def test_irrelevant_block_downgraded(self):
        # أول نص (المشكلة) باتجاه، والاقتباسات باتجاه عمودي => تشابه 0 => الإيقاف بدون دليل ذو صلة
        retrieval.embed_many = lambda texts, batch=16: [[1.0, 0.0]] + [[0.0, 1.0]] * (len(texts) - 1)
        sc = scenarios.load("s1_student_data_offshore")
        co = coordinator.Coordinator(sc)
        co.run()
        recs = audit.read_log(co.log.path)
        do = [r["payload"] for r in recs if r["type"] == "agent_response" and r["actor"] == "data_office"]
        self.assertTrue(do and all(d["verdict"] == "NEED_INFO" and "low_relevance_evidence" in d["flags"] for d in do))
        self.assertNotIn("SUSPEND", [r["payload"]["status"] for r in recs if r["type"] == "decision"])

    def test_expectations_recorded(self):
        sc = scenarios.load("s1_student_data_offshore")
        co = coordinator.Coordinator(sc)
        co.run()
        end = audit.read_log(co.log.path)[-1]["payload"]
        self.assertTrue(end["expectations"] and all(e["pass"] for e in end["expectations"]))

    def test_one_question_round(self):
        sc = scenarios.load("s1_student_data_offshore")
        co = coordinator.Coordinator(sc)
        co.run()
        recs = audit.read_log(co.log.path)
        self.assertEqual(sum(1 for r in recs if r["type"] == "message"), 3)   # سؤال واحد من data_office بكل مرحلة هو فيها

    def test_agent_failure_escalates(self):
        def boom(*a, **k):
            raise llm.LLMError("server down")
        llm.chat = boom
        sc = scenarios.load("s3_outage_policy_update")
        co = coordinator.Coordinator(sc)
        co.run()
        recs = audit.read_log(co.log.path)
        self.assertEqual(co.status, "ESCALATE_TO_HUMAN")
        self.assertTrue(audit.verify_chain(recs)[0])


class TestIngestHelpers(unittest.TestCase):
    def test_chunking_overlap(self):
        text = " ".join(f"w{i}" for i in range(600))
        ch = chunk_text(text)
        self.assertEqual(len(ch[0].split()), 256)
        self.assertEqual(ch[1].split()[0], "w226")

    def test_arabic_pdf_fix(self):
        from governance.itu_ingest import fix_arabic_pdf_text as f
        self.assertEqual(f("املتحكم واملعالج عىل إىل باالشتراك يف ﺣﻮادث"), "المتحكم والمعالج على إلى بالاشتراك في حوادث")
        self.assertEqual(f("Article (22) applies"), "Article (22) applies")
        ok = "هذه نسخة كاملة من القانون وكل الملاحق"
        self.assertEqual(f(ok), ok)                                   # نص سليم ما بيتغيّر

    def test_article_detection(self):
        self.assertEqual(_article_in("... Article (22) Cross-Border ..."), "22")
        self.assertEqual(_article_in("المادة (٤) الموافقة"), "4")
        self.assertEqual(_article_in("المادة الثالثة"), "3")
        from governance.itu_ingest import _article_heads
        t = "Article (2) Scope\nThis applies in accordance with Article 22 to all.\nArticle (3) Consent\nmore"
        self.assertEqual([a for _, a in _article_heads(t)], ["2", "3"])       # الإشارة لمادة 22 مش عنوان

    def test_binding_scope(self):
        from governance.itu_ingest import _scope
        self.assertEqual(_scope("UAE_Data_Protection"), "federal")
        self.assertEqual(_scope("International_Benchmarks"), "international")
        import yaml
        man = yaml.safe_load((Path(__file__).resolve().parents[1] / "knowledge_base" / "policy_docs" / "manifest.yaml").read_text(encoding="utf-8"))
        scopes = {d["id"]: d.get("binding_scope") for d in man["documents"]}
        self.assertEqual(scopes["difc_data_protection_law_5_2020"], "free_zone")
        self.assertTrue(all(scopes.values()))

    def test_unverified_numbers(self):
        from governance.agents import unverified_numbers
        known = "Chat histories are stored for 12 months. Article (22) Cross-Border Transfer"
        self.assertEqual(unverified_numbers("التخزين 12 شهر مخالف، والحد الأقصى ٦ أشهر حسب المادة 22", known), ["6"])
        self.assertEqual(unverified_numbers("store for 12 months", known), [])

    def test_gap_field_validation(self):
        self.assertEqual(coordinator._node("SRC|C|PP|M|P|D|MLFO"), "")
        self.assertEqual(coordinator._node("p"), "P")
        self.assertEqual(coordinator._dimension("AI & Policies (D10)"), "AI & Policies")

    def test_all_scenarios_valid(self):
        self.assertEqual(len([s for s in scenarios.list_all() if "error" not in s]), 4)


if __name__ == "__main__":
    unittest.main()


class TestGuidanceTaintDedupe(unittest.TestCase):
    """تعديلات 4 نوفمبر: الأدلة الإرشادية ما بتوقف، الأرقام المخترعة ما بتنغسل بالرسائل، والتكرار بينشال."""

    def test_guidance_cannot_suspend(self):
        g = {"words": 12, "relevance": 0.8, "binding_scope": "federal_guidance"}
        self.assertFalse(evidence.decisive(g, 0.45))
        self.assertFalse(evidence.decisive(dict(g, binding_scope="emirate_guidance"), 0.45))
        self.assertTrue(evidence.decisive(dict(g, binding_scope="federal"), 0.45))
        r = {"agent": "moe", "verdict": "BLOCK", "_authority": True, "citations_verified": [g], "flags": []}
        self.assertNotEqual(coordinator.decide([r])["status"], "SUSPEND")

    def test_manifest_guidance_split(self):
        import yaml
        man = yaml.safe_load((Path(__file__).resolve().parents[1] / "knowledge_base" / "policy_docs" / "manifest.yaml").read_text(encoding="utf-8"))
        s = {d["id"]: d["binding_scope"] for d in man["documents"]}
        lic = {d["id"]: str(d.get("license", "")) for d in man["documents"]}
        for law in ("uae_pdpl_45_2021_en", "uae_child_digital_safety_26_2025_en"):
            self.assertEqual(s[law], "federal")
        self.assertEqual(s["adek_school_digital_policy_en"], "emirate")
        for g in ("uae_genai_guide_2023_en", "uae_nsai_2031_en", "uae_ai_charter_2024_en"):
            self.assertEqual(s[g], "federal_guidance")
        self.assertEqual(s["dubai_ai_ethics_principles_en"], "emirate_guidance")
        for third_party in ("saudi_nsdai", "singapore_genai_governance_2024", "itu_ai_ready_framework_2025"):
            self.assertNotIn("MIT", lic[third_party])

    def test_tainted_number_not_laundered(self):
        from governance.agents import unverified_numbers
        inbox = "- ANSWER from data_office: provide evidence within 14 days."
        self.assertEqual(unverified_numbers("respond within 14 days", inbox), [])
        self.assertEqual(unverified_numbers("respond within 14 days", inbox, exclude={"14"}), ["14"])

    def test_repeats_dropped(self):
        from governance.agents import Agent
        a = Agent("data_office", {"mandate": "m", "authority": True})
        q = "Can you provide evidence of the impact of the recent knowledge base update on citation accuracy?"
        out = {"stage": 1, "questions": [{"to": "tutor", "question": q}],
               "messages": [{"to": "tutor", "text": "Please provide evidence of the impact of the recent knowledge base update on citation accuracy."},
                            {"to": "moe", "text": "FYI: citation accuracy dropped after the update."}]}
        self.assertEqual(a._drop_repeats(out), 1)                  # NOTIFY مطابق للسؤال لنفس الجهة
        self.assertEqual(len(out["messages"]), 1)
        out2 = {"stage": 1, "questions": [{"to": "tutor", "question": q}], "messages": []}
        self.assertEqual(a._drop_repeats(out2), 1)                 # نفس السؤال بالجولة الثانية لنفس المرحلة
        self.assertEqual(out2["questions"], [])
        out3 = {"stage": 2, "questions": [{"to": "tutor", "question": q}], "messages": []}
        self.assertEqual(a._drop_repeats(out3), 0)                 # مرحلة جديدة: مسموح يرجع يسأل

    def test_coordinator_shares_taint(self):
        sc = scenarios.load("s2_assessment_integrity")
        co = coordinator.Coordinator(sc)
        ids = {id(a.tainted) for a in co.agents.values()}
        self.assertEqual(ids, {id(co.tainted)})


class TestQuantitiesAndArticles(unittest.TestCase):
    def test_duration_needs_unit_match(self):
        from governance.agents import unverified_numbers
        known = "Chat histories are stored for 12 months. Article (6) Consent. Page 6."
        self.assertEqual(unverified_numbers("Reduce storage to 6 months or less", known), ["6"])   # الرقم 6 موجود، بس مش كمدة
        self.assertEqual(unverified_numbers("keep 12 months", known), [])
        self.assertEqual(unverified_numbers("خفّض التخزين إلى ٦ أشهر", known), ["6"])
        self.assertEqual(unverified_numbers("as required by Article 6", known), [])

    def test_article_from_quote_heading(self):
        hits = [{"id": "c1", "text": "Article (11) Scope. Something here. Article (12) Disclosure of Digital Platform Policies "
                 "All Digital Platforms operating in the State shall periodically disclose their user policies.",
                 "dist": 0.3, "meta": {"doc_id": "d", "title": "T", "article": "11", "binding_scope": "federal"}}]
        q = "Article (12) Disclosure of Digital Platform Policies All Digital Platforms operating in the State shall periodically disclose"
        v, r = evidence.verify_citations([{"ref": 1, "quote": q}], hits)
        self.assertEqual(v[0]["article"], "12")
        self.assertEqual(v[0]["article_chunk"], "11")


class TestArabicLamAlef(unittest.TestCase):
    def test_reversed_lam_alef_fixed_safely(self):
        from governance.itu_ingest import fix_arabic_pdf_text as f
        self.assertEqual(f("اإلمارات العربية والمجاالت واألنشطة اآلالت"), "الإمارات العربية والمجالات والأنشطة الآلات")
        for ok in ("كاملة", "مسألة", "القرآن", "الآلة", "الاتصالات", "إلى"):
            self.assertEqual(f(ok), ok)


class TestPrecautionaryRule(unittest.TestCase):
    """R1b (6 نوفمبر): خطر عالي + اقتباس ملزم = إيقاف احترازي، حتى لو القرار NEED_INFO."""
    GOOD = {"words": 12, "relevance": 0.8, "binding_scope": "federal"}

    def r(self, verdict="NEED_INFO", risk="high", scope="federal", auth=True):
        return {"agent": "data_office", "verdict": verdict, "risk": risk, "_authority": auth, "flags": [],
                "citations_verified": [dict(self.GOOD, binding_scope=scope)]}

    def test_high_risk_binding_suspends(self):
        d = coordinator.decide([self.r()])
        self.assertEqual((d["status"], d["rule"]), ("SUSPEND", "R1b"))
        self.assertEqual(coordinator.decide([self.r("CONDITIONS")])["rule"], "R1b")

    def test_no_precaution_without_binding_or_high_risk(self):
        for kw in ({"scope": "federal_guidance"}, {"scope": "free_zone"}, {"risk": "medium"}, {"auth": False}):
            self.assertNotEqual(coordinator.decide([self.r(**kw)])["status"], "SUSPEND", kw)

    def test_block_still_r1(self):
        self.assertEqual(coordinator.decide([self.r("BLOCK")])["rule"], "R1")
