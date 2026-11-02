@echo off
setlocal
cd /d "%~dp0"
echo === OoT3D PT-BR - traducao classica ===
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Ativar-PTBR.ps1"
set "rc=%errorlevel%"
pause
exit /b %rc%
