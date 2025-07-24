import discord
from discord.ui import Button

class SkipButton(Button):
    def __init__(self):
        super().__init__(label="⏭️ Skip", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        view.voice_client.stop()
        await interaction.response.defer() 