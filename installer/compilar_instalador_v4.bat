@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo  OoT3D PT-BR V4 - Compilacao do instalador
echo ============================================
echo.

if not exist "Instalador_GUI_V4.py" (
  echo ERRO: Instalador_GUI_V4.py nao encontrado.
  pause
  exit /b 1
)

if not exist "Instalador_Traducao_PTBR_OoT3D_V4.py" (
  echo ERRO: nucleo V4 nao encontrado.
  pause
  exit /b 1
)

if not exist "TraducaoCompleta\citra\romfs" (
  echo ERRO: TraducaoCompleta\citra\romfs nao encontrada.
  pause
  exit /b 1
)

if not exist "CREDITOS.txt" (
  echo ERRO: CREDITOS.txt nao encontrado.
  pause
  exit /b 1
)

python -m pip install pyinstaller
if errorlevel 1 goto :erro

python -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --name "Traducao PT-BR - Ocarina of Time 3D" ^
  --add-data "Instalador_Traducao_PTBR_OoT3D_V4.py;." ^
  --add-data "CREDITOS.txt;." ^
  --add-data "TraducaoCompleta;TraducaoCompleta" ^
  "Instalador_GUI_V4.py"

if errorlevel 1 goto :erro

echo.
echo SUCESSO!
echo Arquivo criado em:
echo dist\Traducao PT-BR - Ocarina of Time 3D.exe
pause
exit /b 0

:erro
echo.
echo ERRO durante a compilacao.
pause
exit /b 1
