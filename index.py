import discord
from discord.ext import commands
from youtube_dl import YoutubeDL
import time, asyncio
import bs4
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from discord.utils import get
from discord import FFmpegPCMAudio

# 기본 명령어 앞에 !사용
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


@bot.command()
async def play(ctx, *, url):
    YDL_OPRIONS = {"format": "bestaudio", "noplaylist": "True"}
    FFMPEG_OPRIONS = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
    }

    if not vc.is_playing():
        with YoutubeDL(YDL_OPRIONS) as tdl:
            info = tdl.extract_info(url, download=False)
        URL = info["formats"][0]["url"]
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPRIONS))
        await ctx.send(
            embed=discord.Embed(
                title="노래재생", description="현재" + url + "을(를) 재생하고있습니다", color=0x0000CD
            )
        )
    else:
        await ctx.send("Song is already played")


@bot.command()
async def 재생(ctx, *, msg):
    if not vc.is_playing():
        global entireText
        # 기본설정
        YDL_OPTIONS = {"format": "bestaudio", "noplaylist": "True"}
        FFMPEG_OPTIONS = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }

        # chromedriver와 셀레니움을 활용하여 유튜브에서 영상 제목과 링크 등을 가져오는 코드
        chromedriver_dir = "chromedriver.exe"
        driver = webdriver.Chrome(chromedriver_dir)
        driver.get("https://www.youtube.com/results?search_query=" + msg + "+lyrics")
        source = driver.page_source
        bs = bs4.BeautifulSoup(source, "lxml")
        entire = bs.find_all("a", {"id": "video-title"})
        entireNum = entire[0]
        entireText = entireNum.text.strip()
        musicurl = entireNum.get("href")
        url = "https://www.youtube.com" + musicurl

        # 음악 재생부분
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info["formats"][0]["url"]
        await ctx.send(
            embed=discord.Embed(
                title="노래 재생",
                description="현재 " + entireText + "을(를) 재생하고 있습니다.",
                color=0x00FF00,
            )
        )
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
    else:
        await ctx.send("이미 노래가 재생 중이라 노래를 재생할 수 없어요!")


@bot.command()
async def pause(ctx):
    if vc.is_playing():
        vc.pause()
        await ctx.send(
            embed=discord.Embed(
                title="일시정지", description=entireText + "을(를) 일시정지했습니다", color=0x00FF00
            )
        )
    else:
        await ctx.send("Puree is resting")


@bot.command()
async def resume(ctx):
    try:
        vc.resume()
    except:
        await ctx.send("지금 노래가 재생되지 않네요.")
    else:
        await ctx.send(
            embed=discord.Embed(
                title="다시재생", description=entireText + "을(를) 다시 재생했습니다.", color=0x00FF00
            )
        )


@bot.command()
async def stop(ctx):
    if vc.is_playing():
        vc.stop()
        await ctx.send(
            embed=discord.Embed(
                title="노래끄기", description=entireText + "을(를) 종료했습니다", color=0x00FF00
            )
        )
    else:
        await ctx.send("Puree is resting")


bot.run(token)
