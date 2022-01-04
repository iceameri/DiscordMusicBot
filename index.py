import discord
from discord.ext import commands

token = "OTI3NzQwODYwMDY0NDY5MDQz.YdOoAQ.kILYfLhOw0YAf540yWHSqDEPsBk"

bot = commands.Bot(command_prefix="!")


@bot.event
async def on_ready():
    print("Bot Initiating")
    print(bot.user.name)
    print("connetion was succesful")
    await bot.change_presence(status=discord.Status.online, activity=None)


bot.run(token)
