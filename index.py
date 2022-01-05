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

user = []  # 유저가 입력한 노래정보
musictitle = []  # 가공된 정보의 노래 제목
song_queue = []  # 가공된 정보의 노래 링크
musicnow = []  # 현재 출력되는 노래배열


def title(msg):
    global music

    YDL_OPTIONS = {"format": "bestaudio", "noplaylist": "True"}
    FFMPEG_OPTIONS = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        "options": "-vn",
    }

    options = webdriver.ChromeOptions()
    options.add_argument("headless")

    chromedriver_dir = "chromedriver.exe"

    driver = webdriver.Chrome(chromedriver_dir, options=options)
    driver.get("https://www.youtube.com/results?search_query=" + msg + "+lyrics")
    source = driver.page_source
    bs = bs4.BeautifulSoup(source, "lxml")
    entire = bs.find_all("a", {"id": "video-title"})
    entireNum = entire[0]
    music = entireNum.text.strip()

    musictitle.append(music)
    musicnow.append(music)
    test1 = entireNum.get("href")
    url = "https://www.youtube.com" + test1
    with YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
    URL = info["formats"][0]["url"]

    driver.quit()

    return music, URL


def play(ctx):
    global vc
    YDL_OPTIONS = {"format": "bestaudio", "noplaylist": "True"}
    FFMPEG_OPTIONS = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        "options": "-vn",
    }
    URL = song_queue[0]
    del user[0]
    del musictitle[0]
    del song_queue[0]
    vc = get(bot.voice_clients, guild=ctx.guild)
    if not vc.is_playing():
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e: play_next(ctx))


def play_next(ctx):
    if len(musicnow) - len(user) >= 2:
        for i in range(len(musicnow) - len(user) - 1):
            del musicnow[0]
    YDL_OPTIONS = {"format": "bestaudio", "noplaylist": "True"}
    FFMPEG_OPTIONS = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        "options": "-vn",
    }
    if len(user) >= 1:
        if not vc.is_playing():
            del musicnow[0]
            URL = song_queue[0]
            del user[0]
            del musictitle[0]
            del song_queue[0]
            vc.play(
                discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS),
                after=lambda e: play_next(ctx),
            )


@bot.command()
async def 대기열추가(ctx, *, msg):
    user.append(msg)
    result, URLTEST = title(msg)
    song_queue.append(URLTEST)
    await ctx.send(result + "를 재생목록에 추가했어요!")


@bot.command()
async def 대기열삭제(ctx, *, number):
    try:
        ex = len(musicnow) - len(user)
        del user[int(number) - 1]
        del musictitle[int(number) - 1]
        del song_queue[int(number) - 1]
        del musicnow[int(number) - 1 + ex]

        await ctx.send("대기열이 정상적으로 삭제되었습니다.")
    except:
        if len(list) == 0:
            await ctx.send("대기열에 노래가 없어 삭제할 수 없어요!")
        else:
            if len(list) < int(number):
                await ctx.send("숫자의 범위가 목록개수를 벗어났습니다!")
            else:
                await ctx.send("숫자를 입력해주세요!")


@bot.command()
async def 목록(ctx):
    if len(musictitle) == 0:
        await ctx.send("아직 아무노래도 등록하지 않았어요.")
    else:
        global Text
        Text = ""
        for i in range(len(musictitle)):
            Text = Text + "\n" + str(i + 1) + ". " + str(musictitle[i])

        await ctx.send(
            embed=discord.Embed(title="노래목록", description=Text.strip(), color=0x00FF00)
        )


@bot.command()
async def 목록초기화(ctx):
    try:
        ex = len(musicnow) - len(user)
        del user[:]
        del musictitle[:]
        del song_queue[:]
        while True:
            try:
                del musicnow[ex]
            except:
                break
        await ctx.send(
            embed=discord.Embed(
                title="목록초기화",
                description="""목록이 정상적으로 초기화되었습니다. 이제 노래를 등록해볼까요?""",
                color=0x00FF00,
            )
        )
    except:
        await ctx.send("아직 아무노래도 등록하지 않았어요.")


@bot.command()
async def 목록재생(ctx):

    YDL_OPTIONS = {"format": "bestaudio", "noplaylist": "True"}
    FFMPEG_OPTIONS = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        "options": "-vn",
    }

    if len(user) == 0:
        await ctx.send("아직 아무노래도 등록하지 않았어요.")
    else:
        if len(musicnow) - len(user) >= 1:
            for i in range(len(musicnow) - len(user)):
                del musicnow[0]
        if not vc.is_playing():
            play(ctx)
        else:
            await ctx.send("노래가 이미 재생되고 있어요!")


@bot.event
async def on_ready():
    print("Bot Initiating")
    print(bot.user.name)
    print("connetion was succesful")
    await bot.change_presence(
        # 음악연구 + "하는 중"이 자동으로 붙음
        status=discord.Status.online,
        activity=discord.Game("음악연구"),
    )


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
async def url(ctx, *, url):
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
        # 검색할때 크롬창 안보이게하기
        options = webdriver.ChromeOptions()
        options.add_argument("headless")

        global entireText
        # 기본설정
        YDL_OPTIONS = {"format": "bestaudio", "noplaylist": "True"}
        FFMPEG_OPTIONS = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }

        # chromedriver와 셀레니움을 활용하여 유튜브에서 영상 제목과 링크 등을 가져오는 코드
        chromedriver_dir = "chromedriver.exe"
        driver = webdriver.Chrome(chromedriver_dir, options=options)
        driver.get("https://www.youtube.com/results?search_query=" + msg + "+lyrics")
        source = driver.page_source
        bs = bs4.BeautifulSoup(source, "lxml")
        entire = bs.find_all("a", {"id": "video-title"})
        entireNum = entire[0]
        entireText = entireNum.text.strip()
        musicurl = entireNum.get("href")
        url = "https://www.youtube.com" + musicurl

        driver.quit()

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
async def 멜론차트(ctx):
    if not vc.is_playing():
        # 검색할때 크롬창 안보이게하기
        options = webdriver.ChromeOptions()
        options.add_argument("headless")

        global entireText
        # 기본설정
        YDL_OPTIONS = {"format": "bestaudio", "noplaylist": "True"}
        FFMPEG_OPTIONS = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }

        # chromedriver와 셀레니움을 활용하여 유튜브에서 영상 제목과 링크 등을 가져오는 코드
        chromedriver_dir = "chromedriver.exe"
        driver = webdriver.Chrome(chromedriver_dir, options=options)
        driver.get("https://www.youtube.com/results?search_query=멜론차트")
        source = driver.page_source
        bs = bs4.BeautifulSoup(source, "lxml")
        entire = bs.find_all("a", {"id": "video-title"})
        entireNum = entire[0]
        entireText = entireNum.text.strip()
        musicurl = entireNum.get("href")
        url = "https://www.youtube.com" + musicurl

        driver.quit()

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


@bot.command()
async def 지금노래(ctx):
    if not vc.is_playing():
        await ctx.send("Puree is resting")
    else:
        await ctx.send(
            embed=discord.Embed(
                title="지금노래",
                description="현재" + entireText + "을(를) 재생하고 잇습니다.",
                color=0x00FF00,
            )
        )


bot.run(token)
