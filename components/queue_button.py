import discord
from discord.ui import Button

class QueueButton(Button):
    def __init__(self):
        super().__init__(label="📃 Queue", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        if view.queue:
            queue_titles = [title for _, title, _ in view.queue]
            queue_text = "\n".join(f"{idx+1}. {title}" for idx, title in enumerate(queue_titles))
            await interaction.response.send_message(
                f"**Próximas músicas na fila:**\n{queue_text}", ephemeral=True
            )
        else:
            await interaction.response.send_message("A fila está vazia.", ephemeral=True) 