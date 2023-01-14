import datetime
from io import BytesIO
from typing import Any, Optional, Tuple
from urllib.parse import urlparse

import aiohttp
import discord
import yarl
from redbot.core import Config, commands
from redbot.core.bot import Red

from .constants import (INVIDIOUS_DOMAIN, TIKTOK_DESKTOP_PATTERN,
                        TIKTOK_MOBILE_PATTERN, YOUTUBE_PATTERN, ydl)
from .utilities import sync_as_async


class XCali(commands.Cog):
    """Who knows?"""

    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=0x28411747)
        self.session = aiohttp.ClientSession()

    def cog_unload(self) -> None:
        self.bot.loop.create_task(self.session.close())

    def _extract_video_id(self, url: str) -> Optional[str]:
        """
        Extracts the video ID from a YouTube URL.
        """
        match = YOUTUBE_PATTERN.search(url)
        if match:
            return match["id"]

    async def _get_video_info(self, video_id: str) -> Optional[dict]:
        """
        Gets the video info from the Invidious API.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
        }
        async with self.session.get(
            f"https://{INVIDIOUS_DOMAIN}/api/v1/videos/{video_id}?local=true",
            headers=headers,
        ) as response:
            if response.status == 200:
                return await response.json()

    async def _download_file(self, url: str, filename: str) -> Tuple[int, discord.File]:
        async with self.session.get(url, allow_redirects=True, timeout=300) as response:
            if response.status != 200:
                return
            data = await response.read()
            return len(data), discord.File(BytesIO(data), filename)

    async def _extract_video_info(
        self, url: yarl.URL
    ) -> dict[str, Any] | None:
        info = await sync_as_async(self.bot, ydl.extract_info, str(url), download=False)

        if not info:
            return

        return info

    def find_proper_url(self, video_info: dict) -> str:
        for format in video_info["formats"]:
            if format["format_id"] == "download_addr-0":
                return format
        # not found, search for the next best one
        for format in video_info["formats"]:
            if format["url"].startswith("http://api"):
                return format
        # not found, return the first one
        return video_info["formats"][0]

    @commands.Cog.listener("on_message")
    async def on_youtube_trigger(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        if message.guild is None:
            return
        if not message.channel.permissions_for(message.guild.me).attach_files:
            return
        video_id = self._extract_video_id(message.content)
        if not video_id:
            return
        async with message.channel.typing():
            video_info = await self._get_video_info(video_id)
            if not video_info:
                return
            embed = discord.Embed(color=0x2F3136)
            embed.title = video_info["title"]
            embed.set_author(
                name=video_info["author"],
                icon_url=video_info["authorThumbnails"][-1]["url"],
                url=f"https://youtube.com/{video_info['authorUrl']}",
            )
            embed.description = video_info["description"].split("\n")[0]
            embed.set_footer(
                text=f"views: {video_info['viewCount']:,} | likes: {video_info['likeCount']:,}"
            )
            urls = []
            for video_format in video_info["formatStreams"]:
                if not video_format.get("container") or not video_format.get("encoding"):
                    continue
                urls.append(video_format)
            limit = message.guild.filesize_limit
            video = [i for i in urls if i["container"] == "mp4"]
            if not video:
                return
            video = video[0]
            if "clen" in video.keys() and int(video["clen"]) > limit:
                return
            count, dlvideo = await self._download_file(video["url"], f"yt.{video['container']}")
            if count > limit:
                return
            await message.channel.send(
                embed=embed,
                file=dlvideo,
                reference=message.to_reference(fail_if_not_exists=False),
                mention_author=False,
            )

    @commands.Cog.listener("on_message")
    async def on_tiktok_trigger(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        if message.guild is None:
            return
        if not message.channel.permissions_for(message.guild.me).attach_files:
            return
        if match := TIKTOK_MOBILE_PATTERN.search(message.content):
            url = match[1]
        elif match := TIKTOK_DESKTOP_PATTERN.search(message.content):
            url = match[1]
        else:
            return
        url = yarl.URL(url)
        async with message.channel.typing():
            info = await self._extract_video_info(url)
            if not info:
                return
            filesize_limit = (message.guild and message.guild.filesize_limit) or 8388608
            count, dlvideo = await self._download_file(
                self.find_proper_url(info)["url"], f"tiktok.{info['ext']}"
            )
            if count > filesize_limit:
                return
            embed = discord.Embed(color=0x2F3136)
            embed.title = info["title"]
            embed.set_author(name=info["uploader"], url=info["uploader_url"])
            embed.description = info["description"]
            embed.timestamp = datetime.datetime.now(datetime.timezone.utc)
            embed.set_footer(
                text=f"❤️ {info['like_count']:,} | 💬 {info['comment_count']:,} | 📺 {info['view_count']:,} | 🔁 {info['repost_count']:,}"
            )
            await message.channel.send(
                embed=embed,
                file=dlvideo,
                reference=message.to_reference(fail_if_not_exists=False),
                mention_author=False,
            )


async def setup(bot: Red) -> None:
    bot.add_cog(XCali(bot))
