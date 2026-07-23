# Colocar o bot 24/7 na Oracle Cloud (Always Free, custo R$ 0)

O bot só faz conexões de saída (Telegram + Groq), então **não precisa abrir
nenhuma porta**. Uma VM ARM pequena da camada gratuita sobra.

## Parte 1 — Conta Oracle Cloud (navegador, ~15 min)

1. Acesse https://www.oracle.com/br/cloud/free/ e clique em "Comece gratuitamente".
2. Cadastro: e-mail, país **Brasil**, e um **cartão** (só validação; a camada
   Always Free não cobra). Confirme por e-mail/SMS.
3. Na escolha da **região base**, prefira `Brazil Southeast (Vinhedo)` ou
   `Brazil East (São Paulo)`. Se der falta de capacidade ARM depois, uma conta
   nova em `US East (Ashburn)` costuma ter mais máquina livre.

## Parte 2 — Criar a VM ARM gratuita (~10 min)

1. Menu ☰ → **Compute** → **Instances** → **Create instance**.
2. **Image**: Canonical **Ubuntu 22.04** (aarch64/ARM).
3. **Shape**: mude para **Ampere** → `VM.Standard.A1.Flex` →
   **1 OCPU** e **6 GB** de memória (tudo dentro do Always Free; alocação
   pequena tem mais chance de ter capacidade).
4. **SSH keys**: escolha "Generate a key pair for me" e **baixe a chave privada**
   (arquivo `.key`). Guarde bem.
5. **Create**. Quando ficar "Running", anote o **Public IP address**.

> Se aparecer "Out of capacity" ao criar: troque a Availability Domain (AD-1/2/3),
> ou tente de novo mais tarde, ou crie a conta em Ashburn. É o gargalo conhecido
> da Oracle — persistência resolve.

## Parte 3 — Entrar na VM por SSH

No PowerShell (troque o caminho da chave e o IP):

```powershell
icacls "$env:USERPROFILE\Downloads\ssh-key.key" /inheritance:r /grant:r "$($env:USERNAME):(R)"
ssh -i "$env:USERPROFILE\Downloads\ssh-key.key" ubuntu@SEU_IP_PUBLICO
```

(O `icacls` restringe a permissão da chave; sem isso o SSH recusa por segurança.)

## Parte 4 — Instalar o bot (dentro da VM)

O repositório é privado, então clone com autenticação primeiro. Quando o
`git clone` pedir **senha**, cole um **token do GitHub** (crie em github.com →
Settings → Developer settings → Fine-grained tokens → acesso de leitura ao
repo `agentes`); o usuário é `filtroazul`.

```bash
sudo apt-get update -y && sudo apt-get install -y git
git clone https://filtroazul@github.com/filtroazul/agentes.git ~/agentes
bash ~/agentes/deploy/setup.sh      # instala deps e o ambiente virtual
```

Depois, configure as chaves e ligue o serviço (uma vez só):

```bash
cd ~/agentes
sudo cp deploy/leadiot-bot.env.example /etc/leadiot-bot.env
sudo nano /etc/leadiot-bot.env        # cole GROQ_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
sudo cp deploy/leadiot-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now leadiot-bot
```

## Parte 5 — Conferir

```bash
systemctl status leadiot-bot     # deve dizer: active (running)
journalctl -u leadiot-bot -f     # logs ao vivo (Ctrl+C pra sair)
```

Mande uma mensagem pro **@leadiot_bot** no Telegram: ele responde mesmo com o
seu PC desligado. Reinicia a VM? O `systemd` sobe o bot sozinho.

## Comandos do dia a dia

```bash
sudo systemctl restart leadiot-bot   # aplicar mudança de chave
cd ~/agentes && git pull && sudo systemctl restart leadiot-bot   # atualizar o código
```
