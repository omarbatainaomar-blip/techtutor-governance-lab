@echo off
REM Scenarios only (no KB rebuild): S1-S4 with the current knowledge base (Ollama, about 3 hours on CPU)
cd /d "%~dp0"
call .venv\Scripts\activate
set OLLAMA_NUM_GPU=0
set LLM_PROVIDER=ollama
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
if not exist logs mkdir logs
echo [%date% %time%] start >> logs\scenarios.log
echo Running s1...
python run_scenario.py s1_student_data_offshore >> logs\scenarios.log 2>&1
echo Running s2...
python run_scenario.py s2_assessment_integrity >> logs\scenarios.log 2>&1
echo Running s3...
python run_scenario.py s3_outage_policy_update >> logs\scenarios.log 2>&1
echo Running s4...
python run_scenario.py s4_ads_student_profiling >> logs\scenarios.log 2>&1
echo [%date% %time%] ALL DONE >> logs\scenarios.log
echo Done. See logs\scenarios.log
pause
