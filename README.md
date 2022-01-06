# 디스코드 뮤직봇 만들기

## 기본구성

index.py

```jsx
import discord
from discord.ext import commands

#기본 명령어 앞에 !사용
bot = commands.Bot(command_prefix="!")

token = "{토큰명}"

@bot.event
async def on_ready():
    print("Bot Initiating")
    print(bot.user.name)
    print("connetion was succesful")
    await bot.change_presence(status=discord.Status.online, activity=None)

bot.run(token)
```

tokenInfo.py(개발예정)

```jsx
token = "{토큰명}";
```

.gitignore

#[https://www.toptal.com/developers/gitignore에서](https://www.toptal.com/developers/gitignore%EC%97%90%EC%84%9C) 기본 gitignore생성

```jsx
#2022-01-04 add
tokenInfo.py
```

---

## 봇 불러오기 / 내보내기

> pip install pynacl

![Untitled](/images/README_IMAGE/Untitled.png)

#명령어 !join !out

```jsx
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
```

---

## 음악플레이어 셋업 pip 추가 설치 / ffmpeg

> pip install selenium

> pip install beautifulsoup4

> pip install youtube_dl

> pip install requests

\*selenium : 크롤링 프레임워크

로그인 해야만 볼 수 잇는 페이지를 긁어온다거나 할 때 사용하기 위해서 동적 페이지라고 할지라도 HTTP request를 이용하면 원하는 값을 가져올 수 있다

### ffmpeg 설치

[https://www.ffmpeg.org/](https://www.ffmpeg.org/) -download - Windows builds from gyan.dev

![Untitled](/images/README_IMAGE/Untitled%201.png)

ffmpeg full 다운

![Untitled](/images/README_IMAGE/Untitled%202.png)

압축해제후 경로복사하여 path에 추가

> ..\ffmpeg-4.4.1-full_build\bin

path가 정확히 잡혔는지 확인

![Untitled](/images/README_IMAGE/Untitled%203.png)

---

## URL 노래재생

```jsx
import discord
from discord.ext import commands
from youtube_dl import YoutubeDL
import time, asyncio
import bs4
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from discord.utils import get
from discord import FFmpegPCMAudio
```

```jsx
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
```

![Untitled](/images/README_IMAGE/Untitled%204.png)

---

## 검색 후 노래 재생

[https://chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads)

![Untitled](/images/README_IMAGE/Untitled%205.png)

크롬 버전에 맞는 ChromeDriver 다운로드 맞는 버전이 없는 경우 해당 버전에 근접하는 버전다운

### 셀레니움 크롤링을 위한 lxml 설치

> pip install lxml

![Untitled](/images/README_IMAGE/Untitled%206.png)

```jsx
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
```

![Untitled](/images/README_IMAGE/Untitled%207.png)

---

## pause / resume / stop

```jsx
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
```

![Untitled](/images/README_IMAGE/Untitled%208.png)

---

## 봇 상태 변경 / 검색할때 크롬창 안보이게하기 / 멜론차트

```jsx
@bot.event
async def on_ready():
    print("Bot Initiating")
    print(bot.user.name)
    print("connetion was succesful")
    await bot.change_presence(
        status=discord.Status.online, activity=discord.Game("음악연구")
    )
```

![Untitled](/images/README_IMAGE/Untitled%209.png)

```jsx
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
```

![Untitled](/images/README_IMAGE/Untitled%2010.png)

```jsx
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
```

![Untitled](/images/README_IMAGE/Untitled%2011.png)

---

## 대기열 목록 명령어 만들기

```jsx
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
```

---

## 명령어

```jsx
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
!대기열삭제 [숫자] -> 대기열에서 입력한 숫자에 해당하는 노래를 지웁니다.""",
            color=0x00FF00,
        )
    )
```

---

## 자동으로 대기열추가

else 파트만 수정

```jsx
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
        user.append(msg)
        result, URLTEST = title(msg)
        song_queue.append(URLTEST)
        await ctx.send("이미 노래가 재생 중이라 " + result + "을(를) 대기열로 추가시켰어요!")
```

---

# 서버에 올리기

[Heroku](https://dashboard.heroku.com/apps) 가입

![Untitled](/images/README_IMAGE/Untitled%2012.png)

![Untitled](/images/README_IMAGE/Untitled%2013.png)

**Settings - Buildpacks 설정**

![Untitled](/images/README_IMAGE/Untitled%2014.png)

> https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git

> https://github.com/xrisk/heroku-opus.git

> https://github.com/heroku/heroku-buildpack-chromedriver

> https://github.com/heroku/heroku-buildpack-google-chrome

**Deploy - Deployment method - GitHub 연동**

연동후 해당 프로젝트연결

![Untitled](/images/README_IMAGE/Untitled%2015.png)

## 서버이용을 위해 필수파일 생성

\*최상위폴더에 생성

**Procfile** (확장자명 없음) \*띄어쓰기 주의

```jsx
worker:(작성한 코드 파일명.확장자)
worker: python index.py
```

![Untitled](/images/README_IMAGE/Untitled%2016.png)

**requirements.txt**

\*2022 10월 버전없이 작동(버전없이 작동하는 것이 10년넘은것으로 확인됨)

```jsx
asyncio;
selenium;
discord.py[voice];
pip;
beautifulsoup4;
youtube - dl;
ffmpeg - python;
requests;
lxml;
urllib3;
Options;
```

![Untitled](/images/README_IMAGE/Untitled%2017.png)

Aptfile (확장자명없음)

```jsx
git;
```

![Untitled](/images/README_IMAGE/Untitled%2018.png)

**runtime.txt**

[여기](https://devcenter.heroku.com/articles/python-support) 에서 Heroku가 작동하는 runtime python버전 확인

```jsx
python-3.8.12
```

---

## 서버용 코드수정

token의 경우 중요한 정보이기 때문에 config파일에 따로 관리해야하지만 Heroku에서 기본적으로 제공해주는 Config Vars를 이용 (Settings - Config Vars)

![Untitled](/images/README_IMAGE/Untitled%2019.png)

> Key : CHROME_EXECUTABLE_PATH / Values : /app/.chromedriver/bin/chromedriver

> Key : GOOGLE_CHROME_BIN / Values : /app/.apt/usr/bin/google-chrome

> Key : DISCORD_TOKEN / Values : 봇토큰

**index.py**

```jsx
token = os.environ.get("DISCORD_TOKEN");
```

```jsx
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
```

> @bot.event
> async def on_ready(): 에서 opus 를 더 이상 등록하지 않아도 된다

[여기](https://github.com/xrisk/heroku-opus) 에서 확인

![Untitled](/images/README_IMAGE/Untitled%2020.png)

---

## 서버 구동

정상적으로 파일이 올라간 경우 Overview에서 확인가능하다

![Untitled](/images/README_IMAGE/Untitled%2021.png)

![Untitled](/images/README_IMAGE/Untitled%2022.png)

서버를 켜면 봇이 켜지는 것을 확인 할 수 있다

![Untitled](/images/README_IMAGE/Untitled%2023.png)

![Untitled](/images/README_IMAGE/Untitled%2024.png)

![Untitled](/images/README_IMAGE/Untitled%2025.png)

정상작동 확인 (글 작성은 다음날 진행함)

![Untitled](/images/README_IMAGE/Untitled%2026.png)

### 24시간 구동

Heroku 자체에서 매일 서버가 꺼지기 때문에

[https://elements.heroku.com/addons](https://elements.heroku.com/addons) 에서 스케쥴러 사용(계정정보에서 카드등록하면 사용가능)

![Untitled](/images/README_IMAGE/Untitled%2027.png)

![Untitled](/images/README_IMAGE/Untitled%2028.png)

![Untitled](/images/README_IMAGE/Untitled%2029.png)

![Untitled](/images/README_IMAGE/Untitled%2030.png)

Save Job을하게 되면 자동으로 서버가 돌아감

출처

[https://todaycode.tistory.com/5?category=979456](https://todaycode.tistory.com/5?category=979456)

[https://www.youtube.com/channel/UCYEGcpvvVkVhrogOI-VNxhw](https://www.youtube.com/channel/UCYEGcpvvVkVhrogOI-VNxhw)

[https://devcenter.heroku.com/articles/python-support](https://devcenter.heroku.com/articles/python-support)

[https://todaycode.tistory.com/22](https://todaycode.tistory.com/22)
