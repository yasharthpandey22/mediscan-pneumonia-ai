@echo off
title MediScan AI Diagnostic Portal
echo ========================================================
echo        Starting MediScan AI Diagnostic System...
echo ========================================================
echo.
cd /d "%~dp0"
call .venv\Scripts\activate.bat
streamlit run app.py --server.port 8501 --server.headless false
pause
