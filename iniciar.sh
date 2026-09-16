#!/bin/bash
cd "$(dirname "$0")"
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

# Detener cualquier instancia anterior del servidor en el puerto 5000
OLD_PID=$(ss -tlnp 2>/dev/null | grep ':5000' | grep -oP 'pid=\K[0-9]+' | head -1)
if [ -n "$OLD_PID" ]; then
    echo "[INFO] Deteniendo instancia anterior del servidor (PID $OLD_PID)..."
    kill -9 "$OLD_PID" 2>/dev/null
    sleep 1
fi

# Fallback: matar procesos python3 de app.py que sigan vivos
pkill -9 -f "/home/harold/Escritorio/cargueCeder/app.py" 2>/dev/null
sleep 1

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
