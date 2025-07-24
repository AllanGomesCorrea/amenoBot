# Bot Discord

## 1. Configuração Inicial no Discord Developer Portal

1. Acesse o [Discord Developer Portal](https://discord.com/developers/applications).
2. Clique em "New Application" e dê um nome ao seu bot.
3. No menu lateral, vá em "Bot" e clique em "Add Bot".
4. Copie o **Token** do bot (você vai usar no .env).
5. Em "Privileged Gateway Intents", ative:
   - Presence Intent
   - Server Members Intent
   - Message Content Intent
6. Em "OAuth2" > "URL Generator":
   - Marque os scopes: `bot`
   - Em "Bot Permissions", marque:
     - `Administrator`
   - Copie o link gerado e use para adicionar o bot ao seu servidor.

## 2. Crie o arquivo `.env`

Na raiz do projeto, crie um arquivo chamado `.env` com o conteúdo:

```
BOT_TOKEN=SEU_TOKEN_AQUI
```

Substitua `SEU_TOKEN_AQUI` pelo token copiado do portal do Discord.

## 3. Instale as dependências

Com o Python 3.11+ e o virtualenv ativado, execute:

```bash
pip install -r requirements.txt
```

Além disso, instale o **ffmpeg** no seu sistema:
- **macOS:** `brew install ffmpeg`
- **Ubuntu/Debian:** `sudo apt install ffmpeg`
- **Windows:** [Baixe aqui](https://ffmpeg.org/download.html) e adicione ao PATH

## 4. Execute o bot

```bash
python main.py
```

## 5. Comandos disponíveis

### Música
- `/add_song <url>` — Adiciona uma música do YouTube à fila e começa a tocar.
- `/play_pause` — Alterna entre tocar e pausar a música atual.
- `/skip` — Pula para a próxima música da fila.
- `/queue` — Mostra a fila de músicas.
- `/exit` — Remove o bot do canal de voz e limpa a fila.

### /now_playing
Mostra a música que está tocando no momento no canal de voz.
- Exibe o título e o link da música atual.
- Se não houver música tocando, informa que nenhuma música está tocando agora.

### Outros
- `/hello` — Mensagem de boas-vindas.

## 6. Observações
- O bot precisa de permissões de "Conectar" e "Falar" no canal de voz.
- O bot funciona em múltiplos servidores, cada um com sua própria fila de músicas.

---

Se tiver dúvidas, consulte o código ou abra uma issue!

---

## Autor

[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/allancorrea/)
[![GitHub](https://img.shields.io/badge/GitHub-black?logo=github&logoColor=white)](https://github.com/AllanGomesCorrea) 