import discord
from discord.ui import Button
from repository.music_favorite_repository import favorite_repo, extract_youtube_identifier

class StarButton(Button):
    def __init__(self, get_current_song):
        super().__init__(emoji='⭐', style=discord.ButtonStyle.primary)
        self.get_current_song = get_current_song

    async def callback(self, interaction):
        song = self.get_current_song()
        if not song:
            await interaction.response.send_message('Nenhuma música tocando para favoritar.', ephemeral=True)
            return
        title, url = song
        identifier = extract_youtube_identifier(url)
        if favorite_repo.exists(identifier):
            await interaction.response.send_message('Esta música já está nos favoritos!', ephemeral=True)
        else:
            favorite_repo.add(identifier, url, title)
            await interaction.response.send_message('Música adicionada aos favoritos! ⭐', ephemeral=True) 