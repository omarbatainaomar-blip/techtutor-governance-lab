@echo off
cd /d "%~dp0"
call .venv\Scripts\activate
set OLLAMA_NUM_GPU=0
if "%~1"=="" (python run_scenario.py --list) else (python run_scenario.py %*)
pause
