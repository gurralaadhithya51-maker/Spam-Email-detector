@echo off
title Stop Spam Detector Web UI
echo Stopping Spam Detector Web UI Server...
echo.

:: Find the process ID listening on port 5000 and kill it
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5000" ^| find "LISTENING"') do (
    echo Terminating server process (PID %%a)...
    taskkill /F /PID %%a
)

echo.
echo ========================================================
echo Web UI server has been completely stopped.
echo ========================================================
echo.
pause
exit
