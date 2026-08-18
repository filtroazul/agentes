#!/usr/bin/env bash
# Instala o ngrok e o sobe como serviço, expondo o webhook local (porta 8000)
# num domínio HTTPS fixo. Não guarda segredos: recebe token e domínio como args.
#
# Uso:  bash ngrok-setup.sh <AUTHTOKEN> <DOMINIO.ngrok-free.dev>
set -euo pipefail

TOKEN="${1:?informe o authtoken do ngrok como 1o argumento}"
DOMINIO="${2:?informe o dominio fixo (ex: nome.ngrok-free.dev) como 2o argumento}"

# 1. Instala o binário do ngrok (se ainda não tiver)
if ! command -v ngrok >/dev/null 2>&1; then
  echo ">> Baixando ngrok..."
  curl -sL https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz -o /tmp/ngrok.tgz
  sudo tar -xzf /tmp/ngrok.tgz -C /usr/local/bin
fi
echo ">> ngrok: $(ngrok --version)"

# 2. Registra o authtoken (fica em ~/.config/ngrok/ngrok.yml do usuário atual)
ngrok config add-authtoken "$TOKEN"

# 3. Serviço systemd: túnel HTTPS fixo -> webhook local na porta 8000
sudo tee /etc/systemd/system/leadiot-ngrok.service >/dev/null <<UNIT
[Unit]
Description=ngrok tunnel para o webhook LeadIoT (ManyChat)
After=network-online.target leadiot-webhook.service
Wants=network-online.target

[Service]
Type=simple
User=${USER}
ExecStart=/usr/local/bin/ngrok http 8000 --url=https://${DOMINIO} --log=stdout
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT

sudo systemctl daemon-reload
sudo systemctl enable --now leadiot-ngrok
sleep 4
echo ">> status ngrok: $(systemctl is-active leadiot-ngrok)"
echo ">> URL publica: https://${DOMINIO}"
