@echo off
setlocal
cd /d "%~dp0"

echo ===============================================
echo OoT3D PT-BR TriAevum v1.0 - Gerar EXE
echo ===============================================
echo.

where py >nul 2>nul
if errorlevel 1 (
    echo [ERRO] Python nao foi encontrado.
    echo Instale Python 3 para Windows e marque "Add Python to PATH".
    pause
    exit /b 1
)

echo [1/3] Instalando/atualizando PyInstaller...
py -m pip install --upgrade pyinstaller
if errorlevel 1 goto :erro

echo.
echo [2/3] Limpando compilacoes anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo [3/3] Gerando executavel unico...
py -m PyInstaller --noconfirm --clean OoT3D_PTBR_TriAevum_v1.0.spec
if errorlevel 1 goto :erro

echo.
echo ===============================================
echo CONCLUIDO
echo EXE: dist\OoT3D_PTBR_TriAevum_v1.0.exe
echo ===============================================
explorer "%~dp0dist"
pause
exit /b 0

:erro
echo.
echo [ERRO] A compilacao nao foi concluida.
pause
exit /b 1
