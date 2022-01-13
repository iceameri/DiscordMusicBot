# 기본설정
YDL_OPTIONS = {"format": "bestaudio", "noplaylist": "True"}
FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}


class document:
    def __init__(self):
        self
