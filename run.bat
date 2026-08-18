@echo off
:: ============================================================
::  run.bat  --  Launch the Robot Command Simulator
::  Double-click this file to start the app.
:: ============================================================
echo.
echo  ██████╗  ██████╗ ██████╗  ██████╗ ████████╗
echo  ██╔══██╗██╔═══██╗██╔══██╗██╔═══██╗╚══██╔══╝
echo  ██████╔╝██║   ██║██████╔╝██║   ██║   ██║
echo  ██╔══██╗██║   ██║██╔══██╗██║   ██║   ██║
echo  ██║  ██║╚██████╔╝██████╔╝╚██████╔╝   ██║
echo  ╚═╝  ╚═╝ ╚═════╝ ╚═════╝  ╚═════╝   ╚═╝
echo.
echo  Robot Command Simulator  ^|  Compiler Design Project
echo  Developed by: Md. Zihad Hosain Siyam
echo  ============================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python is not installed or not in PATH.
    echo  Please install Python from https://python.org
    pause
    exit /b 1
)

echo  [OK] Python found.
echo  [>>] Launching Robot Command Simulator...
echo.

python "%~dp0frontend\app.py"

if errorlevel 1 (
    echo.
    echo  [ERROR] The application exited with an error.
    pause
)
