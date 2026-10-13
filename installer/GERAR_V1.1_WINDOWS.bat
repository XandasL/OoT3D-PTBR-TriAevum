@echo off
setlocal
cd /d "%~dp0\.."
py -3 -m venv .venv-build
if errorlevel 1 goto :erro
.venv-build\Scripts\python.exe -m pip install -r installer\requirements-build.txt
if errorlevel 1 goto :erro
.venv-build\Scripts\python.exe installer\build_installer.py
if errorlevel 1 goto :erro
echo Pacote v1.1 em artifacts\. A release publica nao foi alterada.
pause
exit /b 0
:erro
echo Falha no build. Confira o log acima.
pause
exit /b 1
