# Mapping TechTutor Governance Lab to ITU-T Y.3172 and the ITU AI Readiness Framework 2.0

Y.3172 pipeline: SRC → C → PP → M → P → D → SINK, orchestrated by the MLFO, validated in an ML Sandbox. Note: Y.3172 targets ML in future networks (IMT-2020); this project uses its architecture *as an analogy* for an education AI pipeline and its sandbox concept as a governance test bed. Official text: https://www.itu.int/rec/T-REC-Y.3172

| Y.3172 node | In this project | Code | Readiness dimension(s) (Framework 2.0) |
|---|---|---|---|
| **SRC** (source) | Student questions + attached files; official policy documents (UAE laws, charters, education guidance, benchmarks) | `web/app.js`, `fetch_policy_docs.py`, `knowledge_base/policy_docs/manifest.yaml` | D1 Data/Model Marketplace, D4 Contextualization & Regional Impact |
| **C** (collector) | HTTP API collects chat requests; downloader collects documents with provenance (issuer, year, URL) | `server.py /api/chat`, `fetch_policy_docs.py` | D1, D13 Digital Infrastructure |
| **PP** (pre-processor) | ITU reference parsing + 256/30-word chunking, page and article tagging, bge-m3 embeddings, language detection | `governance/itu_ingest.py`, `ingest.py`, `build_index.py` | D3 Cross-Domain Correlation (Arabic ↔ English retrieval) |
| **M** (model) | Local open-source LLM (qwen2.5 via Ollama); optional Gemini behind one interface | `rag.py`, `governance/llm.py` | D8 Collaboration with AI, Open Source factor |
| **P** (policy) | Evidence gate (verbatim quote verification), regulator agents' verdicts, deterministic decision rules R0–R5, tutor's own `[[NO_ANSWER]]` refusal | `governance/evidence.py`, `governance/coordinator.py`, `rag.py` | **D10 AI & Policies**, D7 Strategy Alignment |
| **D** (distributor) | Decisions and conditions published to the operator; human review flag for SUSPEND / ESCALATE | `coordinator.decide()`, Governance Lab UI | D6 Human Interface, D9 Impacts of Humans in AI Integration |
| **SINK** | Students (tutor answers), operator and authorities (decisions), auditors (logs, reports) | `web/`, `reports/`, `data/audit/` | D5 Level of Integration of AI in Workflows |
| **MLFO** | Coordinator: receives the "intent" (scenario), releases information per stage, routes messages, enforces rules | `governance/coordinator.py` | D7 Strategy Alignment |
| **ML Sandbox** | Progressive error scenarios executed against simulated stakeholders before any real deployment | `scenarios/*.yaml`, `run_scenario.py`, `web/gov.html` | **D10 AI & Policies**, Sandbox factor, D11 AI for Inclusion (Arabic-first) |

Y.3172 high-level requirements addressed:
- **REQ-ML-SPEC** — scenarios and personas are declarative YAML (agents, mandates, retrieval scopes, stage releases).
- **REQ-ML-MNG** — model selection/fallback (`LLM_PROVIDER`, `LLM_FALLBACK`), monitoring through the audit log.
- **REQ-ML-INT** *(by analogy: Y.3172 defines it for ML interfaces in networks; we apply the same idea to agents)* — one JSON protocol for agent outputs and inter-agent messages (`QUESTION` / `ANSWER` / `NOTIFY`).
- **REQ-ML-DEP** — fully local deployment (Ollama + Chroma), optional cloud model behind the same interface.
