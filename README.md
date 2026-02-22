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

### Opcional: Docker:

Docker:
```bash
docker build -t amenobot .
docker run --rm -v $(pwd):/app --env-file .env -d --name amenobot amenobot
```

Docker compose:
```bash
docker compose up -d
```

## 4. Execute o bot

```bash
python main.py
```

## 5. Comandos disponíveis

### Música
- `/add_song <url>` — Adiciona uma música do YouTube à fila e começa a tocar.
- `/play_next <url>` — Adiciona uma música para tocar em seguida (após a atual). Útil para interromper a playlist temporariamente.
- `/favorite_playlist` — Cria uma playlist aleatória com suas músicas favoritas salvas.
- `/search_favorites <palavra>` — Busca músicas nos favoritos cujo título contém a palavra. Mostra resultados com um menu dropdown para escolher e adicionar à fila diretamente.
- `/play_pause` — Alterna entre tocar e pausar a música atual.
- `/skip` — Pula para a próxima música da fila.
- `/queue` — Mostra a fila de músicas.
- `/filter_queue <palavra>` — Busca na fila músicas cujo título contém a palavra (não precisa ser exata; ex.: "gor" encontra "Gorillaz - Feel Good Inc...").
- `/remove_song_from_queue <posição>` — Remove uma música da fila pela posição (1 = próxima a tocar).
- `/now_playing` — Mostra a música que está tocando agora (título, link e controles).
- `/exit` — Remove o bot do canal de voz e limpa a fila.

### Outros
- `/hello` — Mensagem de boas-vindas.
- `/comandos` — Lista todos os comandos do bot com uma explicação resumida.

## 6. Observações
- O bot precisa de permissões de "Conectar" e "Falar" no canal de voz.
- O bot funciona em múltiplos servidores, cada um com sua própria fila de músicas.
- Use o botão ⭐ nas músicas para adicioná-las aos favoritos.
- O comando `/favorite_playlist` busca todas as músicas favoritadas da base de dados e cria uma fila aleatória sem repetições.

---

Se tiver dúvidas, consulte o código ou abra uma issue!

---

## Autor

[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/allancorrea/)
[![GitHub](https://img.shields.io/badge/GitHub-black?logo=github&logoColor=white)](https://github.com/AllanGomesCorrea)
