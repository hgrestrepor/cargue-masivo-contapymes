#!/usr/bin/env bash
# Instala/actualiza el servicio de systemd (usuario) para que app.py arranque
# solo con el equipo y se reinicie si se cae. No requiere sudo.
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
SVC_DIR="$HOME/.config/systemd/user"
SVC_FILE="$SVC_DIR/cargueceder.service"

mkdir -p "$SVC_DIR"
sed "s|__DIR__|$DIR|g" "$DIR/cargueceder.service" > "$SVC_FILE"

systemctl --user daemon-reload
systemctl --user enable --now cargueceder.service
systemctl --user restart cargueceder.service

sleep 3
echo "Estado: $(systemctl --user is-enabled cargueceder.service) / $(systemctl --user is-active cargueceder.service)"
echo "Logs:   journalctl --user -u cargueceder -n 20 --no-pager"
echo "Probar: http://localhost:5000  (otro equipo: http://$(hostname -I | awk '{print $1}'):5000)"
