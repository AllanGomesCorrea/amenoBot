import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
import yt_dlp
import asyncio
from components.star_button import StarButton
from components.play_pause_button import PlayPauseButton
from components.skip_button import SkipButton
from components.queue_button import QueueButton
from repository.music_favorite_repository import favorite_repo
# Fila de músicas por guild
song_queues = {}

# Histórico de músicas por guild (para skip back)
song_history = {}

# Lock por guild para evitar play_next_song concorrente (evita skip em cascata)
play_locks = {}

def get_play_lock(guild_id):
    if guild_id not in play_locks:
        play_locks[guild_id] = asyncio.Lock()
    return play_locks[guild_id]

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
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        'extract_flat': False,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
        'youtube_include_dash_manifest': False,
        'youtube_include_hls_manifest': False,
        'extractor_retries': 3,
        'fragment_retries': 3,
        'retries': 3,
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
        self.add_item(PlayPauseButton())
        self.add_item(SkipButton())
        self.add_item(QueueButton())
        self.add_item(StarButton(self.get_current_song))

    def get_current_song(self):
        if self.history:
            return self.history[-1]
        return None

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

@app_commands.command(name="play_next", description="Adiciona uma música para tocar em seguida (após a atual).")
@app_commands.describe(url="Link do YouTube")
async def play_next(interaction: discord.Interaction, url: str):
    await interaction.response.defer(ephemeral=False)
    user = interaction.user
    if not user.voice or not user.voice.channel:
        await interaction.followup.send("Você precisa estar em um canal de voz!", ephemeral=True)
        return

    queue = get_song_queue(interaction.guild.id)
    history = get_song_history(interaction.guild.id)
    # Armazene apenas o título e a URL original na fila
    audio_url, title = await get_audio_url(url)
    # Insere na posição 0 para tocar em seguida
    queue.insert(0, (title, url))

    if not interaction.guild.voice_client:
        vc = await user.voice.channel.connect()
    else:
        vc = interaction.guild.voice_client

    await interaction.followup.send(f"Adicionado para tocar em seguida: **{title}**", ephemeral=False)

    bot = interaction.client
    loop = bot.loop

    if not vc.is_playing() and not vc.is_paused():
        await play_next_song(interaction, vc, queue, history, loop)

@app_commands.command(name="favorite_playlist", description="Cria uma playlist aleatória com suas músicas favoritas.")
async def favorite_playlist(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=False)
    user = interaction.user
    if not user.voice or not user.voice.channel:
        await interaction.followup.send("Você precisa estar em um canal de voz!", ephemeral=True)
        return

    # Busca todas as músicas favoritas de forma aleatória
    favorites = favorite_repo.get_random_favorites_playlist()
    
    if not favorites:
        await interaction.followup.send("Você não tem músicas favoritas salvas!", ephemeral=False)
        return

    queue = get_song_queue(interaction.guild.id)
    history = get_song_history(interaction.guild.id)
    
    # Limpa a fila atual e adiciona as músicas favoritas
    queue.clear()
    for identifier, url, title in favorites:
        queue.append((title, url))

    if not interaction.guild.voice_client:
        vc = await user.voice.channel.connect()
    else:
        vc = interaction.guild.voice_client

    await interaction.followup.send(f"🎵 **Playlist de Favoritos criada!**\n📝 **{len(favorites)} músicas** adicionadas à fila de forma aleatória.", ephemeral=True)

    bot = interaction.client
    loop = bot.loop

    if not vc.is_playing() and not vc.is_paused():
        await play_next_song(interaction, vc, queue, history, loop)

async def play_next_song(interaction, vc, queue, history, loop):
    guild_id = interaction.guild.id
    async with get_play_lock(guild_id):
        if not queue:
            await vc.disconnect()
            return
        # Pegue o título e a URL original da fila
        title, url = queue.pop(0)
        # Re-extraia o link de áudio imediatamente antes de tocar
        try:
            audio_url, _ = await get_audio_url(url)
        except Exception as e:
            print(f"[play_next_song] Erro ao obter áudio para {url}: {e}")
            asyncio.run_coroutine_threadsafe(
                play_next_song(interaction, vc, queue, history, loop),
                loop
            )
            return
        if not audio_url or not audio_url.strip():
            print(f"[play_next_song] URL de áudio vazia para: {title}")
            asyncio.run_coroutine_threadsafe(
                play_next_song(interaction, vc, queue, history, loop),
                loop
            )
            return
        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn -c:a libopus -b:a 96k',
        }
        try:
            source = await discord.FFmpegOpusAudio.from_probe(audio_url, **ffmpeg_options)
        except Exception as e:
            print(f"[play_next_song] Erro ao criar fonte para '{title}': {e}")
            asyncio.run_coroutine_threadsafe(
                play_next_song(interaction, vc, queue, history, loop),
                loop
            )
            return
        history.append((title, url))

        def after_playing(error):
            if error:
                print(f"[after_playing] Erro na reprodução de '{title}': {error}")
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
        await interaction.response.send_message("Música pausada.", ephemeral=False)
    elif vc.is_paused():
        vc.resume()
        await interaction.response.send_message("Música retomada.", ephemeral=False)
    else:
        await interaction.response.send_message("Nenhuma música está tocando.", ephemeral=True)

@app_commands.command(name="skip", description="Pula para a próxima música da fila.")
async def skip(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if not vc or not vc.is_playing():
        await interaction.response.send_message("Nenhuma música está tocando.", ephemeral=True)
        return
    vc.stop()
    await interaction.response.send_message("Pulando para a próxima música...", ephemeral=False)

@app_commands.command(name="queue", description="Mostra a fila de músicas.")
async def queue(interaction: discord.Interaction):
    queue = get_song_queue(interaction.guild.id)
    if queue:
        queue_titles = [title for title, _ in queue]
        queue_text = "\n".join(f"{idx+1}. {title}" for idx, title in enumerate(queue_titles))
        await interaction.response.send_message(
            f"**Próximas músicas na fila:**\n{queue_text}", ephemeral=False
        )
    else:
        await interaction.response.send_message("A fila está vazia.", ephemeral=True)

@app_commands.command(name="remove_song_from_queue", description="Remove uma música da fila pela posição.")
@app_commands.describe(position="Posição na fila (1 = próxima música a tocar)")
async def remove_song_from_queue(interaction: discord.Interaction, position: int):
    queue = get_song_queue(interaction.guild.id)
    if not queue:
        await interaction.response.send_message("A fila está vazia.", ephemeral=True)
        return
    if position < 1 or position > len(queue):
        await interaction.response.send_message(
            f"Posição inválida. Use um número entre 1 e {len(queue)}. Use `/queue` para ver a fila.",
            ephemeral=True
        )
        return
    title, url = queue.pop(position - 1)
    await interaction.response.send_message(f"Música removida da fila: **{title}**", ephemeral=False)

@app_commands.command(name="now_playing", description="Mostra a música que está tocando agora.")
async def now_playing(interaction: discord.Interaction):
    history = get_song_history(interaction.guild.id)
    if history and len(history) > 0:
        title, url = history[-1]
        queue = get_song_queue(interaction.guild.id)
        view = MusicPlayerView(interaction, interaction.guild.voice_client, queue, history)
        await interaction.response.send_message(f"🎶 Tocando agora: **{title}**\n{url}", view=view, ephemeral=False)
    else:
        await interaction.response.send_message("Nenhuma música está tocando agora.", ephemeral=True)

@app_commands.command(name="exit", description="Remove o bot do canal de voz e limpa a fila.")
async def exit(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if not vc:
        await interaction.response.send_message("O bot não está em um canal de voz.", ephemeral=True)
        return
    await vc.disconnect(force=True)
    guild_id = interaction.guild.id
    song_queues.pop(guild_id, None)
    song_history.pop(guild_id, None)
    play_locks.pop(guild_id, None)
    await interaction.response.send_message("Bot removido do canal de voz e fila apagada.", ephemeral=False)
