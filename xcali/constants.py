import re

import yt_dlp

ydl = yt_dlp.YoutubeDL({"outtmpl": "buffer/%(id)s.%(ext)s", "quiet": True})

INVIDIOUS_DOMAIN: str = "inv.riverside.rocks"

TIKTOK_MOBILE_PATTERN: re.Pattern[str] = re.compile(
    r"\<?(https?://(?:vt|vm|www)\.tiktok\.com/(?:t/)?[a-zA-Z\d]+\/?)(?:\/\?.*\>?)?\>?"  # noqa
)

TIKTOK_DESKTOP_PATTERN: re.Pattern[str] = re.compile(
    r"\<?(https?://(?:www\.)?tiktok\.com/@(?P<user>.*)/video/(?P<video_id>\d+))(\?(?:.*))?\>?"  # noqa
)

YOUTUBE_PATTERN: re.Pattern[str] = re.compile(
    r"(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=|shorts\/)?(?P<id>[A-Za-z0-9\-=_]{11})"  # noqa
)
