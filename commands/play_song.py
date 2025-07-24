import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
import yt_dlp
import asyncio

# Fila de músicas por guild
song_queues = {}

# Histórico de músicas por guild (para skip back)
song_history = {}

def get_song_queue(guild_id):
    if guild_id not in song_queues:
        song_queues[guild_id] = []
    return song_queues[guild_id]

def get_song_history(guild_id):
    if guild_id not in song_history:
        song_history[guild_id] = []
    return song_history[guild_id]

async def get_audio_url(youtube_url):
    ydl_opts = {
        'format': 'bestaudio[abr<=96]/bestaudio','quiet': True,
        'noplaylist': True,
        'youtube_include_dash_manifest': False,
        'youtube_include_hls_manifest': False,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        return info['url'], info['title']

class MusicPlayerView(View):
    def __init__(self, interaction, voice_client, queue, history):
        super().__init__(timeout=None)
        self.interaction = interaction
        self.voice_client = voice_client
        self.queue = queue
        self.history = history

    @discord.ui.button(label="⏯️ Play/Pause", style=discord.ButtonStyle.primary)
    async def play_pause(self, interaction: discord.Interaction, button: Button):
        if self.voice_client.is_playing():
            self.voice_client.pause()
        elif self.voice_client.is_paused():
            self.voice_client.resume()
        await interaction.response.defer()

    @discord.ui.button(label="⏭️ Skip", style=discord.ButtonStyle.secondary)
    async def skip(self, interaction: discord.Interaction, button: Button):
        self.voice_client.stop()
        await interaction.response.defer()

    @discord.ui.button(label="📃 Queue", style=discord.ButtonStyle.secondary)
    async def show_queue(self, interaction: discord.Interaction, button: Button):
        if self.queue:
            queue_titles = [title for _, title, _ in self.queue]
            queue_text = "\n".join(f"{idx+1}. {title}" for idx, title in enumerate(queue_titles))
            await interaction.response.send_message(
                f"**Próximas músicas na fila:**\n{queue_text}", ephemeral=True
            )
        else:
            await interaction.response.send_message("A fila está vazia.", ephemeral=True)

@app_commands.command(name="add_song", description="Toque uma música do YouTube na call com fila e controles.")
@app_commands.describe(url="Link do YouTube")
async def add_song(interaction: discord.Interaction, url: str):
    await interaction.response.defer(ephemeral=False)
    user = interaction.user
    if not user.voice or not user.voice.channel:
        await interaction.followup.send("Você precisa estar em um canal de voz!", ephemeral=True)
        return

    queue = get_song_queue(interaction.guild.id)
    history = get_song_history(interaction.guild.id)
    # Armazene apenas o título e a URL original na fila
    audio_url, title = await get_audio_url(url)
    queue.append((title, url))

    if not interaction.guild.voice_client:
        vc = await user.voice.channel.connect()
    else:
        vc = interaction.guild.voice_client

    await interaction.followup.send(f"Adicionado à fila: **{title}**", ephemeral=True)

    bot = interaction.client
    loop = bot.loop

    if not vc.is_playing() and not vc.is_paused():
        await play_next_song(interaction, vc, queue, history, loop)

async def play_next_song(interaction, vc, queue, history, loop):
    if not queue:
        await vc.disconnect()
        return
    # Pegue o título e a URL original da fila
    title, url = queue.pop(0)
    # Re-extraia o link de áudio imediatamente antes de tocar
    audio_url, _ = await get_audio_url(url)
    history.append((title, url))
    
    ffmpeg_options = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn -c:a libopus -b:a 96k',
    }
    
    source = await discord.FFmpegOpusAudio.from_probe(audio_url, **ffmpeg_options)

    def after_playing(error):
        fut = asyncio.run_coroutine_threadsafe(
            play_next_song(interaction, vc, queue, history, loop),
            loop
        )
        try:
            fut.result()
        except Exception as e:
            print(f"Erro ao tocar próxima música: {e}")

    vc.play(source, after=after_playing)
    view = MusicPlayerView(interaction, vc, queue, history)
    coro = interaction.followup.send(f"Tocando agora: **{title}**\n{url}", view=view, ephemeral=False)
    asyncio.run_coroutine_threadsafe(coro, loop)

@app_commands.command(name="play_pause", description="Alterna entre tocar e pausar a música.")
async def play_pause(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if not vc:
        await interaction.response.send_message("O bot não está em um canal de voz.", ephemeral=True)
        return
    if vc.is_playing():
        vc.pause()
        await interaction.response.send_message("Música pausada.", ephemeral=True)
    elif vc.is_paused():
        vc.resume()
        await interaction.response.send_message("Música retomada.", ephemeral=True)
    else:
        await interaction.response.send_message("Nenhuma música está tocando.", ephemeral=True)

@app_commands.command(name="skip", description="Pula para a próxima música da fila.")
async def skip(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if not vc or not vc.is_playing():
        await interaction.response.send_message("Nenhuma música está tocando.", ephemeral=True)
        return
    vc.stop()
    await interaction.response.send_message("Pulando para a próxima música...", ephemeral=True)

@app_commands.command(name="queue", description="Mostra a fila de músicas.")
async def queue(interaction: discord.Interaction):
    queue = get_song_queue(interaction.guild.id)
    if queue:
        queue_titles = [title for _, title, _ in queue]
        queue_text = "\n".join(f"{idx+1}. {title}" for idx, title in enumerate(queue_titles))
        await interaction.response.send_message(
            f"**Próximas músicas na fila:**\n{queue_text}", ephemeral=True
        )
    else:
        await interaction.response.send_message("A fila está vazia.", ephemeral=True)

@app_commands.command(name="now_playing", description="Mostra a música que está tocando agora.")
async def now_playing(interaction: discord.Interaction):
    history = get_song_history(interaction.guild.id)
    if history and len(history) > 0:
        title, url = history[-1]
        await interaction.response.send_message(f"🎶 Tocando agora: **{title}**\n{url}", ephemeral=True)
    else:
        await interaction.response.send_message("Nenhuma música está tocando agora.", ephemeral=True)

@app_commands.command(name="exit", description="Remove o bot do canal de voz e limpa a fila.")
async def exit(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if not vc:
        await interaction.response.send_message("O bot não está em um canal de voz.", ephemeral=True)
        return
    await vc.disconnect()
    song_queues.pop(interaction.guild.id, None)
    song_history.pop(interaction.guild.id, None)
    await interaction.response.send_message("Bot removido do canal de voz e fila apagada.", ephemeral=True) 