#!/usr/bin/env bash
# Instala o bot Leadiot numa VM Ubuntu (Oracle Cloud Always Free ARM).
# Rode DENTRO da VM:  bash setup.sh
set -euo pipefail

REPO="https://github.com/filtroazul/agentes.git"
DIR="$HOME/agentes"

echo ">> Instalando dependências do sistema..."
sudo apt-get update -y
sudo apt-get install -y python3-venv python3-pip git

echo ">> Baixando o código..."
if [ -d "$DIR/.git" ]; then
  git -C "$DIR" pull
else
  # Repo privado: o git vai pedir usuário e um token (PAT) do GitHub.
  git clone "$REPO" "$DIR"
fi
cd "$DIR"

echo ">> Criando ambiente virtual e instalando pacotes..."
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

echo ""
echo ">> Código pronto em $DIR"
echo ">> Próximos passos (uma vez só):"
echo "   1) sudo nano /etc/leadiot-bot.env        # cole as chaves (ver leadiot-bot.env.example)"
echo "   2) sudo cp deploy/leadiot-bot.service /etc/systemd/system/"
echo "   3) sudo systemctl daemon-reload && sudo systemctl enable --now leadiot-bot"
echo "   4) systemctl status leadiot-bot          # deve aparecer 'active (running)'"
