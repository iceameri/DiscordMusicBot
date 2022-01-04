import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="!")

token = "OTI3NzQwODYwMDY0NDY5MDQz.YdOoAQ.zcd_aSj5JGiiMR3nKk_VQ9IsoLI"


@bot.event
async def on_ready():
    print("Bot Initiating")
    print(bot.user.name)
    print("connetion was succesful")
    await bot.change_presence(status=discord.Status.online, activity=None)


@bot.command()
async def join(ctx):
    try:
        global vc
        vc = await ctx.message.author.voice.channel.connect()
    except:
        try:  # 유저가 접속하지 않았다면 다른 채널에는 없는지 확인한 다음에 있다면 이동(기존사용하던것을 뺏는다)
            await vc.move_to(ctx.message.author.voice.channel)
        except:
            await ctx.send("There is no user in this Channel")


@bot.command()
async def out(ctx):
    try:
        await vc.disconnect()
    except:
        await ctx.send("It is not belonging this channel")


bot.run(token)
