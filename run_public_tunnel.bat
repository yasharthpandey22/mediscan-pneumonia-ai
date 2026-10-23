@echo off
title MediScan AI Public Cloudflare Tunnel
echo ========================================================
echo        Starting Public Tunnel for MediScan AI...
echo ========================================================
echo.
cd /d "%~dp0"
echo Starting tunnel to http://localhost:8501...
echo Look for the https://*.trycloudflare.com link below!
echo.
cloudflared.exe tunnel --url http://localhost:8501
pause
