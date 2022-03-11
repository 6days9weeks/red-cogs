import re
from typing import List

import aiohttp
import discord
from redbot.core import Config, commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import pagify
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu

from .parsers import custom_log_parser, parse_all

guild_config = {"channels": [], "custom_logs": {}}


class McParser(commands.Cog):
    """Parse common errors and send a response on how-to solve."""

    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=0xEAA1E2D8001000, force_registration=True)
        self.channels = {}
        self.customs = {}
        self.session = aiohttp.ClientSession()
        self.config.register_guild(**guild_config)

    def cog_unload(self) -> None:
        self.bot.loop.create_task(self.session.close())

    async def initialize(self) -> None:
        data = await self.config.all_guilds()
        for guild_id, guild_data in data.items():
            self.channels[int(guild_id)] = guild_data["channels"]
            self.customs[int(guild_id)] = guild_data["custom_logs"]

    __author__ = "sora#0666 (696828906191454221)"

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\nAuthor: {self.__author__}"

    async def red_delete_data_for_user(self, *, requester: str, user_id: int) -> None:
        return

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        if message.guild is None:
            return
        if message.channel.id not in self.channels.get(message.guild.id, []):
            return
        regex = re.compile(r"https:/{2}paste.ee/p/[^\s/]+")
        if found := regex.search(message.content):
            async with self.session.get(str(found.group()).replace("/p/", "/r/")) as r:
                log = await r.text()
            data = parse_all(log)
            if self.customs.get(message.guild.id, None):
                data.extend(custom_log_parser(self.customs[message.guild.id], log))
            if len(data) != 0:
                embed = discord.Embed(
                    title="Automated Response: (Warning: Experimental)",
                    color=discord.Color.random(),
                )
                for x in data:
                    embed.add_field(
                        name=x.split()[0], value=x.replace(x.split()[0], ""), inline=False
                    )
                embed.set_footer(
                    icon_url=self.bot.user.avatar_url,
                    text=f"This might not solve your problem, but it could be worth a try.\nTriggered by: {str(message.author)}",
                )
                await message.channel.send(embed=embed)

    @commands.group(name="mcparser")
    @commands.has_permissions(manage_channels=True)
    async def minecraftparser(self, ctx: commands.Context) -> None:
        """Minecraft Parser"""

    @minecraftparser.command(name="add", usage="<channel>")
    async def minecraftparser_add(
        self, ctx: commands.Context, channel: discord.TextChannel
    ) -> None:
        """Add a channel to minecraft parser"""
        if channel.id in self.channels.get(ctx.guild.id, []):
            await ctx.send("Channel already added.")
            return
        if not self.channels.get(ctx.guild.id, []):
            self.channels[ctx.guild.id] = []
        self.channels[ctx.guild.id].append(channel.id)
        async with self.config.guild(ctx.guild).channels() as channels:
            if channel.id not in channels:
                channels.append(channel.id)
        await ctx.send("Channel added.")

    @minecraftparser.command(name="remove", usage="<channel>")
    async def minecraftparser_remove(
        self, ctx: commands.Context, channel: discord.TextChannel
    ) -> None:
        """Remove a channel from minecraft parser"""
        if channel.id not in self.channels.get(ctx.guild.id, []):
            await ctx.send("Channel not added.")
            return
        self.channels[ctx.guild.id].remove(channel.id)
        async with self.config.guild(ctx.guild).channels() as channels:
            if channel.id in channels:
                channels.remove(channel.id)
        await ctx.send("Channel removed.")

    @minecraftparser.command(name="list", usage="<channel>")
    async def minecraftparser_list(self, ctx: commands.Context) -> None:
        """List all channels added to minecraft parser"""
        if not self.channels.get(ctx.guild.id, []):
            await ctx.send("No channels added.")
            return
        await ctx.send(
            "Channels added: "
            + ", ".join(
                str(ctx.guild.get_channel(x).name) for x in self.channels.get(ctx.guild.id, [])
            )
        )

    @minecraftparser.group(name="custom")
    async def minecraftparser_custom(self, ctx: commands.Context) -> None:
        """Custom Minecraft Parser"""

    @minecraftparser_custom.command(name="add")
    async def minecraftparser_custom_add(
        self, ctx: commands.Context, solve: str, trigger: str
    ) -> None:
        """Add a custom log parser"""
        if not self.customs.get(ctx.guild.id):
            self.customs[ctx.guild.id] = {}
        self.customs[ctx.guild.id][solve] = trigger
        async with self.config.guild(ctx.guild).custom_logs() as custom:
            custom[solve] = trigger
        await ctx.send("Custom parser added.")

    @minecraftparser_custom.command(name="list")
    async def minecraftparser_custom_list(self, ctx: commands.Context) -> None:
        """List all custom log parsers"""
        if not self.customs.get(ctx.guild.id):
            await ctx.send("No custom log parsers added.")
            return
        msg = ""
        for x in self.customs.get(ctx.guild.id):
            msg += f"--------------------\n**Caused By:** {self.customs[ctx.guild.id][x]}\n**Solved By:** {x}\n--------------------\n"
        embeds: List[discord.Embed] = []
        for page in pagify(msg):
            embeds.append(
                discord.Embed(
                    description=page, title="Custom Parsers", color=discord.Color.random()
                )
            )
        if len(embeds) == 1:
            await ctx.send(embed=embeds[0])
        else:
            await menu(ctx, embeds, DEFAULT_CONTROLS)

    @minecraftparser_custom.command(name="remove")
    async def minecraftparser_custom_remove(self, ctx: commands.Context, *, solve: str) -> None:
        """Remove a custom log parser"""
        if not self.customs.get(ctx.guild.id):
            await ctx.send("No custom log parsers added.")
            return
        if solve not in self.customs.get(ctx.guild.id):
            await ctx.send("Custom log parser not found.")
            return
        del self.customs[ctx.guild.id][solve]
        async with self.config.guild(ctx.guild).custom_logs() as custom:
            del custom[solve]
        await ctx.send("Custom log parser removed.")


async def setup(bot: Red):
    cog = McParser(bot)
    bot.add_cog(cog)
    await cog.initialize()
