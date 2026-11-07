@echo off
REM Overnight run: FULL rebuild of the policy KB (binding scope, article and Arabic fixes), then all 4 scenarios (Ollama)
cd /d "%~dp0"
call .venv\Scripts\activate
set OLLAMA_NUM_GPU=0
set LLM_PROVIDER=ollama
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
if not exist logs mkdir logs
echo [%date% %time%] start >> logs\overnight.log
echo Rebuilding the policy knowledge base (about 45-60 min)...
python -m governance.itu_ingest >> logs\overnight.log 2>&1
if errorlevel 1 (
  echo [%date% %time%] INGEST FAILED - scenarios not run >> logs\overnight.log
  echo Ingest failed. See logs\overnight.log
  pause
  exit /b 1
)
echo [%date% %time%] ingest done >> logs\overnight.log
echo Running s1...
python run_scenario.py s1_student_data_offshore >> logs\overnight.log 2>&1
echo Running s2...
python run_scenario.py s2_assessment_integrity >> logs\overnight.log 2>&1
echo Running s3...
python run_scenario.py s3_outage_policy_update >> logs\overnight.log 2>&1
echo Running s4...
python run_scenario.py s4_ads_student_profiling >> logs\overnight.log 2>&1
echo [%date% %time%] ALL DONE >> logs\overnight.log
echo Done. See logs\overnight.log
pause
