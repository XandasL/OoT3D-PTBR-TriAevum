@echo off
setlocal
rem OoT3D PT-BR - ativador portatil (codigo aberto).
rem Executa somente o script PowerShell que acompanha este pacote.
rem -NoProfile impede carregar perfis pessoais do PowerShell.
rem -ExecutionPolicy Bypass vale somente para este processo; nao altera
rem a politica permanente do Windows. O script nao acessa a rede.
cd /d "%~dp0"
echo === OoT3D PT-BR - ativador da traducao ===
echo Sera verificada a integridade do mod e ajustado o perfil do TriAevum.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Ativar-PTBR.ps1"
set "rc=%errorlevel%"
if not "%rc%"=="0" echo A ativacao nao foi concluida. Confira a mensagem de erro acima.
pause
exit /b %rc%
