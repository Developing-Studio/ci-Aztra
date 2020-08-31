import discord
from discord.ext import commands
import os

bot = commands.Bot(command_prefix='//')

for ext in filter(lambda x: x.endswith('.py'), os.listdir('./exts')):
    bot.load_extension('exts.' + os.path.splitext(ext)[0])