@echo off
cd /d "%~dp0"
call .venv\Scripts\activate
set OLLAMA_NUM_GPU=0
python -m governance.itu_ingest
pause
