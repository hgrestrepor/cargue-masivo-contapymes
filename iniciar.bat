@echo off
title CargueCeder - Iniciando...
color 0A

echo ============================================
echo   CARGUE CEDER - Inicio automatico
echo ============================================
echo.

:: Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado.
    echo Descargalo desde: https://www.python.org/downloads/
    echo Asegurate de marcar "Add Python to PATH" durante la instalacion.
    echo.
    pause
    exit /b 1
)

echo [OK] Python detectado:
python --version
echo.

:: Instalar dependencias
echo [INFO] Instalando dependencias...
pip install flask bcrypt pandas openpyxl requests --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Fallaron las dependencias. Revisa tu conexion a internet.
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas.
echo.

:: Abrir navegador despues de 3 segundos
start "" /min cmd /c "timeout /t 3 >nul & start http://localhost:5000"

:: Ejecutar app
echo [INFO] Iniciando servidor en http://localhost:5000
echo [INFO] Cierra esta ventana para detener el servidor.
echo.
python app.py
