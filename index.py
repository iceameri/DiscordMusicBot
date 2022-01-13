import discord
from discord.ext import commands
from youtube_dl import YoutubeDL
import time, asyncio
import bs4
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from discord.utils import get
from discord import FFmpegPCMAudio
import os
import Token
from frame import document

# 기본 명령어 앞에 !사용
bot = commands.Bot(command_prefix="!")

# 검색할때 크롬창 안보이게하기
CHROMEOPTIONS = webdriver.ChromeOptions()
CHROMEOPTIONS.add_argument("headless")

# prefix
PREFIX_YOUTUBEURL = "https://www.youtube.com/results?search_query="

# Heroku server TOKEN
# TOKEN = os.environ.get("DISCORD_TOKEN")

# local dev
TOKEN = Token.TOKEN


user = []  # 유저가 입력한 노래정보
musictitle = []  # 가공된 정보의 노래 제목
song_queue = []  # 가공된 정보의 노래 링크
musicnow = []  # 현재 출력되는 노래배열

userF = []  # 유저 정보 저장 배열
userFlist = []  # 유저 개닝 노래 저장 배열
allplaylist = []  # 플레이리스트 배열

number = 1


def title(msg):
    global music

    # Heroku server
    # driver = load_chrome_driver()

    # local dev
    chromedriver_dir = r"chromedriver.exe"
    driver = webdriver.Chrome(chromedriver_dir, options=options)

    driver.get(PREFIX_YOUTUBEURL + msg + "+lyrics")
    source = driver.page_source
    bs = bs4.BeautifulSoup(source, "lxml")
    entire = bs.find_all("a", {"id": "video-title"})
    entireNum = entire[0]
    music = entireNum.text.strip()

    musictitle.append(music)
    musicnow.append(music)
    test1 = entireNum.get("href")
    url = "https://www.youtube.com" + test1
    with YoutubeDL(document.YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
    URL = info["formats"][0]["url"]

    driver.quit()

    return music, URL


def play(ctx):
    global vc

    URL = song_queue[0]
    del user[0]
    del musictitle[0]
    del song_queue[0]
    vc = get(bot.voice_clients, guild=ctx.guild)
    if not vc.is_playing():
        vc.play(
            FFmpegPCMAudio(URL, **document.FFMPEG_OPTIONS),
            after=lambda e: play_next(ctx),
        )


def play_next(ctx):
    if len(musicnow) - len(user) >= 2:
        for i in range(len(musicnow) - len(user) - 1):
            del musicnow[0]

    if len(user) >= 1:
        if not vc.is_playing():
            del musicnow[0]
            URL = song_queue[0]
            del user[0]
            del musictitle[0]
            del song_queue[0]
            vc.play(
                discord.FFmpegPCMAudio(URL, **document.FFMPEG_OPTIONS),
                after=lambda e: play_next(ctx),
            )


def again(ctx, url):
    global number

    if number:
        with YoutubeDL(document.YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info["formats"][0]["url"]
        if not vc.is_playing():
            vc.play(
                FFmpegPCMAudio(URL, **document.FFMPEG_OPTIONS),
                after=lambda e: again(ctx, url),
            )


def URLPLAY(url):
    if not vc.is_playing():
        with YoutubeDL(document.YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info["formats"][0]["url"]
        vc.play(FFmpegPCMAudio(URL, **document.FFMPEG_OPTIONS))
        client.loop.create_task(subtitle_song(ctx, URL))


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


@bot.command()
async def 즐겨찾기(ctx):
    global Ftext
    Ftext = ""
    correct = 0
    global Flist
    for i in range(len(userF)):
        if userF[i] == str(ctx.message.author.name):  # userF에 유저정보가 있는지 확인
            correct = 1  # 있으면 넘김
    if correct == 0:
        userF.append(str(ctx.message.author.name))  # userF에다가 유저정보를 저장
        userFlist.append([])  # 유저 노래 정보 첫번째에 유저이름을 저장하는 리스트를 만듬.
        userFlist[len(userFlist) - 1].append(str(ctx.message.author.name))

    for i in range(len(userFlist)):
        if userFlist[i][0] == str(ctx.message.author.name):
            if len(userFlist[i]) >= 2:  # 노래가 있다면
                for j in range(1, len(userFlist[i])):
                    Ftext = Ftext + "\n" + str(j) + ". " + str(userFlist[i][j])
                titlename = str(ctx.message.author.name) + "님의 즐겨찾기"
                embed = discord.Embed(
                    title=titlename, description=Ftext.strip(), color=0x00FF00
                )
                embed.add_field(
                    name="목록에 추가\U0001F4E5",
                    value="즐겨찾기에 모든 곡들을 목록에 추가합니다.",
                    inline=False,
                )
                embed.add_field(
                    name="플레이리스트로 추가\U0001F4DD",
                    value="즐겨찾기에 모든 곡들을 새로운 플레이리스트로 저장합니다.",
                    inline=False,
                )
                Flist = await ctx.send(embed=embed)
                await Flist.add_reaction("\U0001F4E5")
                await Flist.add_reaction("\U0001F4DD")
            else:
                await ctx.send("아직 등록하신 즐겨찾기가 없어요.")


@bot.command()
async def 즐겨찾기추가(ctx, *, msg):
    correct = 0
    for i in range(len(userF)):
        if userF[i] == str(ctx.message.author.name):  # userF에 유저정보가 있는지 확인
            correct = 1  # 있으면 넘김
    if correct == 0:
        userF.append(str(ctx.message.author.name))  # userF에다가 유저정보를 저장
        userFlist.append([])  # 유저 노래 정보 첫번째에 유저이름을 저장하는 리스트를 만듦.
        userFlist[len(userFlist) - 1].append(str(ctx.message.author.name))

    for i in range(len(userFlist)):
        if userFlist[i][0] == str(ctx.message.author.name):
            chromedriver_dir = r"D:\Discord_Bot\chromedriver.exe"
            driver = webdriver.Chrome(chromedriver_dir, options=options)
            driver.get(PREFIX_YOUTUBEURL + msg + "+lyrics")
            source = driver.page_source
            bs = bs4.BeautifulSoup(source, "lxml")
            entire = bs.find_all("a", {"id": "video-title"})
            entireNum = entire[0]
            music = entireNum.text.strip()

            driver.quit()

            userFlist[i].append(music)
            await ctx.send(music + "(이)가 정상적으로 등록되었어요!")


@bot.command()
async def 즐겨찾기삭제(ctx, *, number):
    correct = 0
    for i in range(len(userF)):
        if userF[i] == str(ctx.message.author.name):  # userF에 유저정보가 있는지 확인
            correct = 1  # 있으면 넘김
    if correct == 0:
        userF.append(str(ctx.message.author.name))  # userF에다가 유저정보를 저장
        userFlist.append([])  # 유저 노래 정보 첫번째에 유저이름을 저장하는 리스트를 만듦.
        userFlist[len(userFlist) - 1].append(str(ctx.message.author.name))

    for i in range(len(userFlist)):
        if userFlist[i][0] == str(ctx.message.author.name):
            if len(userFlist[i]) >= 2:  # 노래가 있다면
                try:
                    del userFlist[i][int(number)]
                    await ctx.send("정상적으로 삭제되었습니다.")
                except:
                    await ctx.send("입력한 숫자가 잘못되었거나 즐겨찾기의 범위를 초과하였습니다.")
            else:
                await ctx.send("즐겨찾기에 노래가 없어서 지울 수 없어요!")


def load_chrome_driver():
    options = webdriver.ChromeOptions()

    options.binary_location = os.getenv("GOOGLE_CHROME_BIN")

    options.add_argument("--headless")
    # options.add_argument('--disable-gpu')
    options.add_argument("--no-sandbox")

    return webdriver.Chrome(
        executable_path=str(os.environ.get("CHROME_EXECUTABLE_PATH")),
        chrome_options=options,
    )


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


@bot.event
async def on_reaction_add(reaction, users):
    if users.bot == 1:
        pass
    else:
        try:
            await Flist.delete()
        except:
            pass
        else:
            if str(reaction.emoji) == "\U0001F4E5":
                await reaction.message.channel.send(
                    "잠시만 기다려주세요. (즐겨찾기 갯수가 많으면 지연될 수 있습니다.)"
                )
                print(users.name)
                for i in range(len(userFlist)):
                    if userFlist[i][0] == str(users.name):
                        for j in range(1, len(userFlist[i])):
                            try:
                                driver.close()
                            except:
                                print("NOT CLOSED")

                            user.append(userFlist[i][j])
                            result, URLTEST = title(userFlist[i][j])
                            song_queue.append(URLTEST)
                            await reaction.message.channel.send(
                                userFlist[i][j] + "를 재생목록에 추가했어요!"
                            )
            elif str(reaction.emoji) == "\U0001F4DD":
                await reaction.message.channel.send(
                    "플레이리스트가 나오면 생길 기능이랍니다. 추후에 올릴 영상을 기다려주세요!"
                )

            # 정밀검색추가부분
            elif str(reaction.emoji) == "\u0031\uFE0F\u20E3":
                URLPLAY(rinklist[0])
                await ctx.send("정상적으로 진행되었습니다.")
            elif str(reaction.emoji) == "\u0032\uFE0F\u20E3":
                URLPLAY(rinklist[1])
                await ctx.send("정상적으로 진행되었습니다.")
            elif str(reaction.emoji) == "\u0033\uFE0F\u20E3":
                URLPLAY(rinklist[2])
                await ctx.send("정상적으로 진행되었습니다.")
            elif str(reaction.emoji) == "\u0034\uFE0F\u20E3":
                URLPLAY(rinklist[3])
                await ctx.send("정상적으로 진행되었습니다.")
            elif str(reaction.emoji) == "\u0035\uFE0F\u20E3":
                URLPLAY(rinklist[4])
                await ctx.send("정상적으로 진행되었습니다.")


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
        user.append(msg)
        result, URLTEST = title(msg)
        song_queue.append(URLTEST)
        await ctx.send("이미 노래가 재생 중이라 " + result + "을(를) 대기열로 추가시켰어요!")


@bot.command()
async def 재생(ctx, *, msg):
    if not vc.is_playing():
        global entireText

        # Heroku server
        # driver = load_chrome_driver()

        # local dev
        chromedriver_dir = r"chromedriver.exe"
        driver = webdriver.Chrome(chromedriver_dir, options=CHROMEOPTIONS)

        # chromedriver와 셀레니움을 활용하여 유튜브에서 영상 제목과 링크 등을 가져오는 코드
        driver.get(PREFIX_YOUTUBEURL + msg + "+lyrics")
        source = driver.page_source
        bs = bs4.BeautifulSoup(source, "lxml")
        entire = bs.find_all("a", {"id": "video-title"})
        entireNum = entire[0]
        entireText = entireNum.text.strip()
        musicurl = entireNum.get("href")
        url = "https://www.youtube.com" + musicurl

        driver.quit()

        # 음악 재생부분
        with YoutubeDL(document.YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info["formats"][0]["url"]
        await ctx.send(
            embed=discord.Embed(
                title="노래 재생",
                description="현재 " + entireText + "을(를) 재생하고 있습니다.",
                color=0x00FF00,
            )
        )
        vc.play(FFmpegPCMAudio(URL, **document.FFMPEG_OPTIONS))
    else:
        user.append(msg)
        result, URLTEST = title(msg)
        song_queue.append(URLTEST)
        await ctx.send("이미 노래가 재생 중이라 " + result + "을(를) 대기열로 추가시켰어요!")


@bot.command()
async def 멜론차트(ctx):
    if not vc.is_playing():

        global entireText

        # chromedriver와 셀레니움을 활용하여 유튜브에서 영상 제목과 링크 등을 가져오는 코드
        # Heroku server
        # driver = load_chrome_driver()

        # local dev
        chromedriver_dir = r"chromedriver.exe"
        driver = webdriver.Chrome(chromedriver_dir, options=options)

        driver.get(PREFIX_YOUTUBEURL + "멜론차트")
        source = driver.page_source
        bs = bs4.BeautifulSoup(source, "lxml")
        entire = bs.find_all("a", {"id": "video-title"})
        entireNum = entire[0]
        entireText = entireNum.text.strip()
        musicurl = entireNum.get("href")
        url = "https://www.youtube.com" + musicurl

        driver.quit()

        # 음악 재생부분
        with YoutubeDL(document.YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info["formats"][0]["url"]
        await ctx.send(
            embed=discord.Embed(
                title="노래 재생",
                description="현재 " + entireText + "을(를) 재생하고 있습니다.",
                color=0x00FF00,
            )
        )
        vc.play(FFmpegPCMAudio(URL, **document.FFMPEG_OPTIONS))
    else:
        await ctx.send("이미 노래가 재생 중이라 노래를 재생할 수 없어요!")


def URLPLAY(url):

    if not vc.is_playing():
        with YoutubeDL(document.YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info["formats"][0]["url"]
        vc.play(FFmpegPCMAudio(URL, **document.FFMPEG_OPTIONS))
        client.loop.create_task(subtitle_song(ctx, URL))


@bot.command()
async def 정밀검색(ctx, *, msg):

    Text = ""
    # global Text
    global rinklist
    global Alist
    rinklist = [0, 0, 0, 0, 0]

    try:
        global vc
        vc = await ctx.message.author.voice.channel.connect()
    except:
        try:
            await vc.move_to(ctx.message.author.voice.channel)
        except:
            await ctx.send("채널에 유저가 접속해있지 않네요..")

    # Heroku server
    # driver = load_chrome_driver()

    # local dev
    chromedriver_dir = r"chromedriver.exe"
    driver = webdriver.Chrome(chromedriver_dir, options=options)

    driver.get(PREFIX_YOUTUBEURL + msg)
    source = driver.page_source
    bs = bs4.BeautifulSoup(source, "lxml")
    entire = bs.find_all("a", {"id": "video-title"})
    for i in range(0, 4):
        entireNum = entire[i]
        entireText = entireNum.text.strip()  # 영상제목
        test1 = entireNum.get("href")  # 하이퍼링크
        rinklist[i] = "https://www.youtube.com" + test1
        Text = Text + str(i + 1) + "번째 영상" + entireText + "\n링크 : " + rinklist[i]

    await ctx.send(
        embed=discord.Embed(
            title="검색한 영상들입니다.", description=Text.strip(), color=0x00FF00
        )
    )
    Alist = await ctx.send(embed=embed)


@bot.command()
async def 반복재생(ctx, *, msg):

    try:
        global vc
        vc = await ctx.message.author.voice.channel.connect()
    except:
        try:
            await vc.move_to(ctx.message.author.voice.channel)
        except:
            pass

    global entireText
    global number
    number = 1

    if len(musicnow) - len(user) >= 1:
        for i in range(len(musicnow) - len(user)):
            del musicnow[0]

    # Heroku server
    # driver = load_chrome_driver()

    # local dev
    chromedriver_dir = r"chromedriver.exe"
    driver = webdriver.Chrome(chromedriver_dir, options=CHROMEOPTIONS)

    driver.get(PREFIX_YOUTUBEURL + msg + "+lyrics")
    source = driver.page_source
    bs = bs4.BeautifulSoup(source, "lxml")
    entire = bs.find_all("a", {"id": "video-title"})
    entireNum = entire[0]
    entireText = entireNum.text.strip()
    musicnow.insert(0, entireText)
    test1 = entireNum.get("href")
    url = "https://www.youtube.com" + test1
    await ctx.send(
        embed=discord.Embed(
            title="반복재생",
            description="현재 " + musicnow[0] + "을(를) 반복재생하고 있습니다.",
            color=0x00FF00,
        )
    )
    again(ctx, url)


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
        global number
        number = 0
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


@bot.command()
async def 스킵(ctx):
    if len(user) > 1:
        if vc.is_playing():
            vc.stop()
            global number
            number = 0
            await ctx.send(
                embed=discord.Embed(
                    title="스킵",
                    description=musicnow[0] + "을(를) 다음에 재생합니다!",
                    color=0x00FF00,
                )
            )

        else:
            await ctx.send("노래가 이미 재생되고 있어요!")
    else:
        await ctx.send("목록에 노래가 2개 이상 없네요..")


@bot.command()
async def 명령어(ctx):
    await ctx.send(
        embed=discord.Embed(
            title="명령어",
            description="""
\n!명령어 -> 뮤직봇의 모든 명령어를 볼 수 있습니다.
\n!join -> 뮤직봇을 자신이 속한 채널로 부릅니다.
\n!out -> 뮤직봇을 자신이 속한 채널에서 내보냅니다.
\n!url [노래링크] -> 유튜브URL를 입력하면 뮤직봇이 노래를 틀어줍니다.
(목록재생에서는 사용할 수 없습니다.)
\n!재생 [노래이름] -> 뮤직봇이 노래를 검색해 틀어줍니다.
\n!stop -> 현재 재생중인 노래를 끕니다.
!pause -> 현재 재생중인 노래를 일시정지시킵니다.
!resume -> 일시정지시킨 노래를 다시 재생합니다.
\n!지금노래 -> 지금 재생되고 있는 노래의 제목을 알려줍니다.
\n!멜론차트 -> 최신 멜론차트를 재생합니다.
\n!즐겨찾기 -> 자신의 즐겨찾기 리스트를 보여줍니다.
!즐겨찾기추가 [노래이름] -> 뮤직봇이 노래를 검색해 즐겨찾기에 추가합니다.
!즐겨찾기삭제 [숫자] ->자신의 즐겨찾기에서 숫자에 해당하는 노래를 지웁니다.
\n!목록 -> 이어서 재생할 노래목록을 보여줍니다.
!목록재생 -> 목록에 추가된 노래를 재생합니다.
!목록초기화 -> 목록에 추가된 모든 노래를 지웁니다.
\n!대기열추가 [노래] -> 노래를 대기열에 추가합니다.
!대기열삭제 [숫자] -> 대기열에서 입력한 숫자에 해당하는 노래를 지웁니다.
\n!반복재생 -> 노래한곡을 반복재생합니다 다른노래를 바꿀경우 재생중인 노래를 멈추고 명령어를 다시 입력해야합니다""",
            color=0x00FF00,
        )
    )


bot.run(TOKEN)
