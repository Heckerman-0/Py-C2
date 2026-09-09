@echo off
title C2 Server Launcher
color 0C

echo ==============================
echo     🔥 C2 Server Launcher
echo ==============================
echo.
echo [*] Starting server on 0.0.0.0:4444 ...
echo.

python server.py

echo.
echo [*] Server has stopped. Press any key to close...
pause >nul
