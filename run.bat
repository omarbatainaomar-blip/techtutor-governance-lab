@echo off
cd /d "%~dp0"
call .venv\Scripts\activate
set OLLAMA_NUM_GPU=0
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
python server.py
pause
