#!/bin/bash
echo "============================================"
echo "  CARGUE CEDER - Inicio automatico"
echo "============================================"
echo

if ! command -v python3 &>/dev/null; then
    echo "[ERROR] Python3 no esta instalado."
    echo "Instalar con: sudo apt install python3 python3-pip"
    exit 1
fi

echo "[OK] Python detectado: $(python3 --version)"
echo

echo "[INFO] Instalando dependencias..."
pip3 install flask bcrypt pandas openpyxl requests --quiet
if [ $? -ne 0 ]; then
    echo "[ERROR] Fallaron las dependencias. Revisa tu conexion a internet."
    exit 1
fi
echo "[OK] Dependencias instaladas."
echo

# Intentar abrir navegador tras 3 segundos
(sleep 3 && xdg-open http://localhost:5000) &>/dev/null &

echo "[INFO] Iniciando servidor en http://localhost:5000"
echo "[INFO] Presiona Ctrl+C para detener el servidor."
echo
python3 app.py
