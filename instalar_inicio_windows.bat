@echo off
setlocal EnableExtensions
title CargueCeder - Arranque automatico
color 0A

for %%I in ("%~dp0.") do set "DIR=%%~fI"
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

echo ============================================
echo   CARGUE CEDER - Arranque automatico
echo ============================================
echo Carpeta: %DIR%
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] No se encontro Python en el PATH.
    echo Instala Python desde https://www.python.org/downloads/windows/
    echo y marca "Add Python to PATH".
    pause
    exit /b 1
)
python --version
echo.

if exist "%DIR%\requirements.txt" (
    echo [INFO] Instalando dependencias...
    python -m pip install -r "%DIR%\requirements.txt" --quiet
    echo [OK] Dependencias listas.
    echo.
)

echo [INFO] Creando acceso automatico en el inicio de sesion de Windows...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$lnk = (New-Object -ComObject WScript.Shell).CreateShortcut('%STARTUP%\CargueCeder.lnk');" ^
  "$lnk.TargetPath = '%DIR%\iniciar.bat';" ^
  "$lnk.WorkingDirectory = '%DIR%';" ^
  "$lnk.Save()"

if exist "%STARTUP%\CargueCeder.lnk" (
    echo [OK] Acceso creado. Windows ejecutara el servidor solo cada vez que inicies sesion.
) else (
    echo [AVISO] No se pudo crear el acceso automatico.
    echo Hazlo a mano: Win+R -^> shell:startup y arrastra un acceso directo de "iniciar.bat" ahi.
)

echo.
echo [INFO] Arrancando el servidor por esta vez...
start "" "%DIR%\iniciar.bat"
timeout /t 5 >nul

echo.
echo ============================================
echo   Listo. Prueba ahora: http://localhost:5000
echo   (otro equipo: http://IP-DE-ESTA-MAQUINA:5000)
echo ============================================
pause
