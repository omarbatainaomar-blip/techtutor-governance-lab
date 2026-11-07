# TechTutor Governance Lab — AI for Good Lab Hackathon: UAE (Education)

A bilingual (Arabic/English) AI tutor for secondary-school computing and AI, **plus** a multi-agent governance
sandbox that decides whether, and under which conditions, the tutor may be deployed in UAE schools.

- The **tutor** answers only from its knowledge base. After the model writes, the system checks every sentence
  against the retrieved passages by meaning and attaches the citations itself; answers that are mostly unsupported
  are replaced by "not found".
- The **governance agents** reason only over a **UAE policy knowledge base** built with the **ITU reference ingestion
  code**. Every quote is machine-verified, decisions come from fixed rules (the model proposes, the rules decide),
  every step goes into a **hash-chained audit log**, and each run ends with a **policy gap analysis** mapped to
  **ITU-T Y.3172** and the **ITU AI Readiness Framework 2.0**.

Everything runs locally (Ollama + Chroma) on a CPU-only laptop. No data leaves the machine unless you opt into Gemini.

> **Simulation notice.** The agents emulate institutional *roles* for testing AI governance. They do not represent
> the official positions of the UAE Ministry of Education, the UAE Data Office, the UAE AI Office or any other body,
> and their outputs are not legal advice. Every decision based on weak evidence is marked for human review.

## Architecture

```
knowledge bases ──► agents / tutor ──► web UI
 tutor KB (374 passages, 7 topics)     TechTutor (rag.py)          chat (index.html)
 policy KB (1,863 passages, 28 docs)   5 governance agents          🏛 Governance Lab (gov.html)
 ITU readiness framework (19 defs)     coordinator + rules R0–R5    live run · replay · downloads
```

| Component | File(s) | Role |
|---|---|---|
| Tutor | `rag.py`, `server.py`, `web/` | bge-m3 + Chroma + qwen2.5:7b; answers only from passages; sentence-level attribution; prompt-injection and harmful-request guards |
| Tutor KB | `knowledge_base/claude_notes/`, `knowledge_base/education_technology_knowledge_base.sqlite` | 374 passages: programming, AI, networking, databases, web security, Git/dev tools, robotics (see *Disclosure*) |
| Policy KB | `governance/itu_ingest.py`, `knowledge_base/policy_docs/manifest.yaml` | ITU reference pipeline (MIT, adapted): page, article number, **binding scope** and licence per passage → Chroma `kb_policy_uae` + `kb_framework` + `policy_kb_export.jsonl` |
| Agents | `governance/agents.py`, `governance/personas.yaml` | TechTutor (solution), Policy & Legal Advisor, Ministry of Education ★, Data Protection Regulator ★, AI Governance Authority ★ (★ = can suspend) |
| Coordinator | `governance/coordinator.py` | Releases information in stages to specific agents only, routes QUESTION/ANSWER/NOTIFY messages (repeats removed), applies rules R0–R5, runs gap analysis with an absence check |
| Evidence gate | `governance/evidence.py` | Verbatim match (Arabic-aware), rejects quotes that drop a negation or change a number, relevance score, article number read from the quoted heading |
| Audit | `governance/audit.py` | JSONL log, SHA-256 hash chain + head index, tamper and truncation detection, `--verify` |
| Scenarios | `scenarios/*.yaml` | Progressive, asymmetric information release, each with machine-scored `expected:` behaviour |

### Binding scope (who can stop the project)

| Scope | Documents | Effect |
|---|---|---|
| `federal`, `emirate` | Federal Decree-Law 45/2021 (PDPL), Federal Decree-Law 26/2025 (Child Digital Safety), Federal Law 15/2020 (Consumer Protection), ADEK School Digital Policy | can justify **SUSPEND** |
| `federal_guidance`, `emirate_guidance` | National AI Strategy 2031, UAE AI Charter, Generative AI Guide, AI Ethics Guidelines, Dubai AI Principles, MoE/ADEK announcements | support conditions only |
| `free_zone` | DIFC Law 5/2020 and Regulation 10, ADGM | comparison only |
| `international`, `standard` | EU AI Act, OECD, UNESCO, UNICEF, Saudi, Singapore, US ED, ITU | benchmark only |

### Decision rules (the LLM proposes, rules decide)

- `R1` an authority BLOCKs with a verified, relevant quote of 8+ words from a **binding** UAE law or school policy → **SUSPEND**
- `R1b` precautionary: an authority rates the risk **high** and backs it with the same kind of binding quote, even if its
  verdict is NEED_INFO or CONDITIONS → **SUSPEND** (added 6 Nov: the 7B model often names a violation but still answers NEED_INFO)
- `R2` an authority needs information, an agent or retrieval failed, or a verdict had no evidence → **ESCALATE_TO_HUMAN**
- `R3` any authority sets conditions → **CONTINUE_WITH_CONDITIONS**
- `R4` all authorities approve with evidence → **CONTINUE**
- `R0` no authority responded → status unchanged
- `R5` a suspension stays until **every** suspending authority approves again with evidence

Within a stage the most restrictive verdict of each agent counts. Numbers (durations, percentages) that do not appear
in the case or the cited text are flagged as possible hallucinations, and a number flagged once stays flagged when
it is repeated by another agent.

## Results (final runs, 6 November 2026)

Model `qwen2.5:7b`, embeddings `bge-m3`, CPU only, policy KB of 1,863 passages. Reports in `reports/`, logs in
`data/audit/` (file names end with the run id below).

| Scenario | Final | Stage decisions | Agent calls | Verified / rejected quotes | Time | Audit chain |
|---|---|---|---|---|---|---|
| S1 student data, minors, offshore model (`2ec6ba`) | SUSPEND | R2 → R4 → R1b → R1b | 21 | 29 / 0 | 48 min | ✅ 52 events |
| S2 exam integrity, wrong content (`acb925`) | ESCALATE_TO_HUMAN | R2 → R2 → R2 | 13 | 12 / 2 | 32 min | ✅ 36 events |
| S3 outage, public chatbot workaround (`a74cee`) | SUSPEND | R2 → R1b → R1b | 19 | 28 / 1 | 39 min | ✅ 51 events |
| S4 in-app purchases, then targeted ads from student chats (`04a0c3`) | SUSPEND | R2 → R1 → R5 | 18 | 23 / 0 | 42 min | ✅ 46 events |

- **S4** (based on the template's error scenario): the Data Protection Regulator issues an explicit BLOCK at stage 2,
  quoting the Child Digital Safety law ("Applying Child privacy and personal data protection features according to
  age group"); the suspension holds at stage 3 (R5).
- **S3**: suspended as a precaution (R1b) when the operator proposes sending students to an unapproved public chatbot.
- **S2**: stays with human review. No binding UAE text covers the accuracy of AI tutor content, which is reported as a
  policy gap.
- **S1, an agent error caught by the checks**: at stage 2 the Data Regulator *approved* although an audit had just found
  Emirates ID numbers in stored chats and an offshore model switch was planned. The scenario's `expected:` check flags
  this stage as failed in the report; the next stage suspends the pilot (R1b). We kept this run unchanged as an
  honest example of a wrong agent verdict and of how the checks expose it.
- Evidence gate in action: 3 quotes were rejected because they changed meaning or were not verbatim.

Earlier runs (2–6 Nov) remain in `data/audit/` as development history; they used earlier code or knowledge base.

**Tutor evaluation** (`eval_topics.py`, 29 questions, log in the report): 26/29 before the last fix. All 8 control
cases passed (out-of-KB questions such as BGP and Kubernetes, off-domain questions, prompt injection, a harmful
request, a follow-up). Two answers were wrongly refused because lead-in sentences ("follow these steps:") were
checked as claims; that was fixed and the PID answer re-tested live. One refusal is correct: the KB has no passage on
Python lists vs tuples. On the attribution calibration set, answers grounded in the sources scored 0.55–1.00 and
answers from model memory 0–0.44 (threshold 0.50). Median answer time is about 100 s on CPU.
Retrieval eval (`eval.py`, 31 Oct): 78/78 questions retrieve the right source or are correctly unanswerable.

Offline tests: `python -m unittest discover tests` → 66 tests, no Ollama needed.

## Limitations

- **Small local model.** qwen2.5:7b on CPU: about 2 minutes per agent call, 35–60 minutes per scenario, about 100 s
  per tutor answer. Arabic output is sometimes awkward (literal translations of technical terms).
- **Attribution checks meaning, not every detail.** It confirms a sentence is supported by a passage, not that facts
  from two places were combined correctly, and it does not check code. Short list items are checked by exact terms.
- **Precautionary rule.** R1b relies on the model's own "high" risk rating, so it can suspend on a weak quote or miss a
  case; every suspension is marked for human review.
- **Agents.** Agents often answer NEED_INFO and ask each other similar questions; the Policy & Legal Advisor rarely
  quotes. Relevance threshold 0.45 lets some weak quotes through (they are flagged, and cannot decide a suspension
  unless they come from a binding text).
- **Coverage.** 14 of the 42 documents in `manifest.yaml` could not be downloaded automatically (including the Arabic
  Child Digital Safety law). No official KHDA AI-in-schools policy or PDPL executive regulation was found; these
  absences are reported as gaps. Some Arabic PDF text still has extraction artefacts.

## Disclosure: AI-assisted content

The tutor knowledge base (`knowledge_base/claude_notes/`, source `SRC017`, 374 passages) consists of study notes
written with an AI assistant (Claude) to give the tutor clear, citable explanations in Arabic and English. In the
chat they appear as "TechTutor study notes" with the section heading used for each answer. The other sources listed in `sources.yaml`
(Wikipedia, d2l.ai and others) are not in the current knowledge base. Parts of the code were also written with AI
assistance.

## Setup (Windows)

```bat
ollama pull bge-m3
ollama pull qwen2.5:7b
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python fetch_policy_docs.py          :: downloads the official documents listed in manifest.yaml
python -m governance.itu_ingest      :: builds kb_policy_uae + kb_framework + policy_kb_export.jsonl
python build_index.py                :: builds the tutor index from the tutor KB
python -m unittest discover tests    :: offline tests
run.bat                              :: web app → http://127.0.0.1:8000  → chat, and "🏛 Governance Lab"
run_all_overnight.bat                :: rebuild policy KB + run S1–S3 (about 3 hours on CPU)
python run_scenario.py --list
python run_scenario.py s1_student_data_offshore [--lang ar]
python run_scenario.py --verify data\audit\<run>.jsonl
python eval_topics.py                :: tutor evaluation across all topics
```

In the Governance Lab, pick a run under *Previous runs* to replay it. Optional Gemini (prompts leave the device):
`set LLM_PROVIDER=gemini` · `set GEMINI_API_KEY=...`. `server.py` env vars: `HOST`, `PORT`, `COOKIE_SECURE=1`,
`OPEN_BROWSER=0`, `OLLAMA_NUM_GPU=0`.

## Submission outputs

- `knowledge_base/policy_kb_export.jsonl` + `policy_kb_summary.json` + `policy_docs/manifest.yaml`: the policy KB as
  text with source, page, article, binding scope and licence. Original documents are not redistributed; the manifest
  links to the official sources.
- `knowledge_base/claude_notes/` + `education_technology_knowledge_base.sqlite`: the tutor KB.
- `knowledge_base/chroma/`: the ready-to-query RAG index (Chroma, bge-m3 embeddings) with three collections:
  `tech` (tutor, 374), `kb_policy_uae` (policy, 1,863) and `kb_framework` (ITU readiness framework, 19).
  `governance/itu_ingest.py` and `build_index.py` rebuild it from the sources.
- `data/audit/*.jsonl`, `reports/*.md`: audit logs and readable run reports.
- `docs/Y3172_mapping.md`, `docs/technical_report_draft.md`.

## Credits and licences

Policy ingestion adapted from the ITU AI for Good reference code (github.com/CrashingGuru/ITUAIReadiness,
© 2026 Vishnu Ram OV, MIT, see `governance/ITU_REFERENCE_LICENSE.txt`). Only that code is under MIT. Policy documents
remain © their issuers; the KB quotes them with attribution for non-commercial research, and each passage carries its
licence in the metadata.
