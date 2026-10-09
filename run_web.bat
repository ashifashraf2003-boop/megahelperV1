@echo off
title USA Phone Validator Web App
echo Starting USA Phone Validator Web Server...
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo Node.js is not found. Running with Python...
    py server.py
) else (
    node server.js
)
pause
