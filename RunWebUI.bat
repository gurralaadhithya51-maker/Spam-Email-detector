@echo off
title Spam Detector Web UI Launcher
echo Starting Spam Detector Web UI...

:: Change to the directory where this batch file is located
cd /d "%~dp0"

:: Activate the Python virtual environment
call .venv\Scripts\activate.bat

:: Start the Flask backend in the background using pythonw (no console window for the server)
echo Starting background server...
start /b pythonw spam-detector\backend\app.py

:: Give the server a couple of seconds to start up
timeout /t 3 /nobreak >nul

:: Open the default web browser
echo Opening web browser...
start http://127.0.0.1:5000/

echo.
echo ========================================================
echo The application is now running in your web browser!
echo The background server process is hidden.
echo To completely stop the server later, use StopWebUI.bat
echo ========================================================
echo.
echo Closing this launcher window in 5 seconds...
timeout /t 5 >nul
exit
