import discord
from discord.ui import Button

class PlayPauseButton(Button):
    def __init__(self):
        super().__init__(label="⏯️ Play/Pause", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        view = self.view  # view é injetado automaticamente pelo discord.py
        if view.voice_client.is_playing():
            view.voice_client.pause()
        elif view.voice_client.is_paused():
            view.voice_client.resume()
        await interaction.response.defer() 