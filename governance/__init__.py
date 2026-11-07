"""Governance Sandbox: multi-agent policy simulation for deploying TechTutor (an AI tutor) in UAE education.

Modules:
  config      settings (env-driven)
  llm         one chat() for Ollama (default, local) or Gemini (optional)
  itu_ingest  policy KB ingestion adapted from ITU's reference code (MIT)
  retrieval   embeddings + policy/framework search
  evidence    verbatim-citation gate
  audit       hash-chained JSONL audit log
  agents      agent personas + message protocol
  coordinator deterministic orchestration, decisions, gap analysis
  scenarios   progressive error-scenario loader
"""
