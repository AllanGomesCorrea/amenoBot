import discord
from discord import app_commands

COMANDOS = [
    ("hello", "Mensagem de boas-vindas."),
    ("add_song", "Adiciona uma música do YouTube ao final da fila."),
    ("play_next", "Adiciona uma música para tocar em seguida (após a atual)."),
    ("favorite_playlist", "Cria uma playlist aleatória com suas músicas favoritas."),
    ("search_favorites", "Busca músicas nos favoritos e permite escolher no menu para adicionar à fila."),
    ("play_pause", "Pausa ou retoma a música atual."),
    ("skip", "Pula para a próxima música da fila."),
    ("queue", "Mostra as próximas músicas na fila."),
    ("filter_queue", "Busca na fila músicas que contêm uma palavra (ex.: gor → Gorillaz)."),
    ("remove_song_from_queue", "Remove uma música da fila pela posição (1 = próxima)."),
    ("now_playing", "Mostra a música que está tocando agora."),
    ("exit", "Remove o bot do canal de voz e limpa a fila."),
    ("comandos", "Lista todos os comandos do bot com explicação resumida."),
]

@app_commands.command(name="comandos", description="Lista todos os comandos do bot com uma explicação resumida.")
async def comandos(interaction: discord.Interaction):
    lines = ["**Comandos disponíveis:**\n"]
    for name, desc in COMANDOS:
        lines.append(f"• `/{name}` — {desc}")
    await interaction.response.send_message("\n".join(lines), ephemeral=True)
