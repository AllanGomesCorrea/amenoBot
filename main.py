import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from commands import register_commands

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN não encontrado no arquivo .env")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} está online!')
    try:
        synced = await bot.tree.sync()
        print(f"Sincronizados {len(synced)} comandos de barra.")
    except Exception as e:
        print(f"Erro ao sincronizar comandos de barra: {e}")

register_commands(bot)

bot.run(BOT_TOKEN)
