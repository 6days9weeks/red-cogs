from typing import List, Optional

import discord
from redbot.core import commands, Config
from redbot.core.bot import Red
from logging import getLogger
from redbot.core.utils import chat_formatting as chat
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu
from redbot.core.utils.predicates import MessagePredicate

from .converters import ActionReason, MemberID

logger = getLogger("red.dia.GlobalBan")


class GlobalBan(commands.Cog):
    """Ban users globally from all servers I'm in."""

    __version__ = "0.0.2"
    __author__ = "dia ♡#0666 (696828906191454221)"

    def format_help_for_context(self, ctx: commands.Context) -> str:
        """Thanks Sinbad."""
        pre_processed = super().format_help_for_context(ctx)
        return (
            f"{pre_processed}\n**Cog Version:** {self.__version__}\n**Author:** {self.__author__}"
        )

    def __init__(self, bot: Red):
        self.bot: Red = bot
        self.config = Config.get_conf(self, identifier=0x33039392, force_registration=True)
        self.config.register_global(**{"banned": []})

    @commands.command()
    @commands.is_owner()
    @commands.guild_only()
    async def globalban(
        self, ctx: commands.Context, user: MemberID, *, reason: Optional[ActionReason] = None
    ) -> None:
        """Ban a user globally from all servers [botname] is in."""
        if not reason:
            reason = f"Global ban by {ctx.author} (ID: {ctx.author.id})"
        async with self.config.banned() as f:
            if user.id not in f:
                f.append(user.id)
        banned_guilds: List[discord.Guild] = []
        couldnt_ban: List[discord.Guild] = []
        for guild in self.bot.guilds:
            try:
                await guild.ban(user, reason=reason)
            except (discord.HTTPException, discord.Forbidden):
                couldnt_ban.append(guild)
            finally:
                banned_guilds.append(guild)
        ctx_sent = await ctx.send(
            embed=discord.Embed(
                description=f"Banned {user} from {len(banned_guilds)}/{len(self.bot.guilds)} guilds.\nRespond with `yes` to see which guilds they were banned in and couldn't be banned in (if applicable)."
            )
        )
        pred = MessagePredicate.yes_or_no(ctx)
        await self.bot.wait_for("message", check=pred)
        if pred.result is False:
            await ctx_sent.edit(
                embed=discord.Embed(
                    description=f"Banned {user} from {len(banned_guilds)}/{len(self.bot.guilds)} guilds."
                )
            )
            return
        if banned_guilds:
            banned_message: str = ""
            banned_pages: List[str] = []
            banned_embeds: List[discord.Embed] = []
            for idx, guild in enumerate(
                sorted(banned_guilds, key=lambda g: g.member_count, reverse=True), 1
            ):
                banned_message += f"{idx}. `{guild.name}` with `{guild.member_count}` members.\n > Owned by [`{guild.owner}`] (`{guild.owner.id}`)\n/20jaajs0b/"
                for page in chat.pagify(banned_message, delims=["/20jaajs0b/"], page_length=1500):
                    banned_pages.append(page)
            for idx, page in enumerate(banned_pages, 1):
                embed = discord.Embed(color=0x2F3136)
                embed.set_author(name=f"Banned {user} from:", icon_url=self.bot.user.avatar_url)
                embed.description = page.replace("/20jaajs0b/", "")
                embed.set_footer(
                    text=f"Page {idx} of {len(banned_guilds)}\nTotal: {len(self.bot.guilds)} servers"
                )
                banned_embeds.append(embed)
            await menu(ctx, banned_embeds, DEFAULT_CONTROLS)
        if couldnt_ban:
            couldnt_message: str = ""
            couldnt_pages: List[str] = []
            couldnt_embeds: List[discord.Embed] = []
            for idx, guild in enumerate(
                sorted(couldnt_ban, key=lambda g: g.member_count, reverse=True), 1
            ):
                couldnt_message += f"{idx}. `{guild.name}` with `{guild.member_count}` members.\n > Owned by [`{guild.owner}`] (`{guild.owner.id}`)\n/20jaajs0b/"
                for page in chat.pagify(couldnt_message, delims=["/20jaajs0b/"]):
                    couldnt_pages.append(page)
            for idx, page in enumerate(couldnt_pages, 1):
                embed = discord.Embed(color=0x2F3136)
                embed.set_author(
                    name=f"Couldn't ban {user} from:", icon_url=self.bot.user.avatar_url
                )
                embed.description = page.replace("/20jaajs0b/", "")
                embed.set_footer(text=f"Page {idx} of {len(couldnt_ban)}")
                couldnt_embeds.append(embed)
            await menu(ctx, couldnt_embeds, DEFAULT_CONTROLS)

    @commands.command()
    @commands.is_owner()
    @commands.guild_only()
    async def globalunban(
        self, ctx: commands.Context, user: MemberID, *, reason: Optional[ActionReason] = None
    ) -> None:
        """Unban a user globally from all servers [botname] is in."""
        if not reason:
            reason = f"Global unban by {ctx.author} (ID: {ctx.author.id})"
        async with self.config.banned() as f:
            if user.id in f:
                f.remove(user.id)
        unbanned_guilds: List[discord.Guild] = []
        couldnt_unban: List[discord.Guild] = []
        for guild in self.bot.guilds:
            try:
                await guild.unban(user, reason=reason)
            except (discord.HTTPException, discord.Forbidden):
                couldnt_unban.append(guild)
            finally:
                unbanned_guilds.append(guild)
        ctx_sent = await ctx.send(
            embed=discord.Embed(
                description=f"Unbanned {user} from {len(unbanned_guilds)}/{len(self.bot.guilds)} guilds.\nRespond with `yes` to see which guilds they were unbanned in and couldn't be unbanned in (if applicable)."
            )
        )
        pred = MessagePredicate.yes_or_no(ctx)
        await self.bot.wait_for("message", check=pred)
        if pred.result is False:
            await ctx_sent.edit(
                embed=discord.Embed(
                    description=f"Unbanned {user} from {len(unbanned_guilds)}/{len(self.bot.guilds)} guilds."
                )
            )
            return
        if unbanned_guilds:
            unbanned_message: str = ""
            unbanned_pages: List[str] = []
            unbanned_embeds: List[discord.Embed] = []
            for idx, guild in enumerate(
                sorted(unbanned_guilds, key=lambda g: g.member_count, reverse=True), 1
            ):
                unbanned_message += f"{idx}. `{guild.name}` with `{guild.member_count}` members.\n > Owned by [`{guild.owner}`] (`{guild.owner.id}`)\n/20jaajs0b/"
                for page in chat.pagify(
                    unbanned_message, delims=["/20jaajs0b/"], page_length=1500
                ):
                    unbanned_pages.append(page)
            for idx, page in enumerate(unbanned_pages, 1):
                embed = discord.Embed(color=0x2F3136)
                embed.set_author(name=f"Unbanned {user} from:", icon_url=self.bot.user.avatar_url)
                embed.description = page.replace("/20jaajs0b/", "")
                embed.set_footer(text=f"Page {idx} of {len(unbanned_guilds)}")
                unbanned_embeds.append(embed)
            await menu(ctx, unbanned_embeds, DEFAULT_CONTROLS)
        if couldnt_unban:
            couldnt_message: str = ""
            couldnt_pages: List[str] = []
            couldnt_embeds: List[discord.Embed] = []
            for idx, guild in enumerate(
                sorted(couldnt_unban, key=lambda g: g.member_count, reverse=True), 1
            ):
                couldnt_message += f"{idx}. `{guild.name}` with `{guild.member_count}` members.\n > Owned by [`{guild.owner}`] (`{guild.owner.id}`)\n/20jaajs0b/"
                for page in chat.pagify(couldnt_message, delims=["/20jaajs0b/"]):
                    couldnt_pages.append(page)
            for idx, page in enumerate(couldnt_pages, 1):
                embed = discord.Embed(color=0x2F3136)
                embed.set_author(
                    name=f"Couldn't unban {user} from:", icon_url=self.bot.user.avatar_url
                )
                embed.description = page.replace("/20jaajs0b/", "")
                embed.set_footer(text=f"Page {idx} of {len(couldnt_unban)}")
                couldnt_embeds.append(embed)
            await menu(ctx, couldnt_embeds, DEFAULT_CONTROLS)

    @commands.command()
    @commands.is_owner()
    @commands.guild_only()
    async def listglobalban(self, ctx: commands.Context) -> None:
        """List all global banned users."""
        message: str = ""
        pages: List[str] = []
        async with self.config.banned() as ff:
            if len(ff) == 0:
                return await ctx.send("No user has been globally banned.")
            for x in ff:
                x = await self.bot.get_or_fetch_user(x)
                message += f"{str(x)} - ({x.id})"
        for page in chat.pagify(message):
            pages.append(page)
        await menu(ctx, pages, DEFAULT_CONTROLS)

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        """
        Ban global banned users auto-fucking-matically
        """
        async with self.config.banned() as f:
            if user.id not in f:
                return
            try:
                await guild.ban(user, reason="Global banned by bot owner.")
            except (discord.HTTPException, discord.Forbidden) as e:
                logger.exception(e)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role) -> None:
        if not after.is_bot_managed():
            return
        if after.members and after.members[0].id != self.bot.user.id:
            return
        if not after.guild.me.guild_permissions.ban_members:
            logger.info(
                f"Leaving {after.guild.name}/{after.guild.id} as they removed ban members permission from me."
            )
            try:
                await after.guild.leave()
            except discord.NotFound:
                return

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member) -> None:
        if after.id != self.bot.user.id:
            return
        if not after.guild_permissions.ban_members:
            logger.info(
                f"Leaving {after.guild.name}/{after.guild.id} as they removed ban members permission from me."
            )
            try:
                await after.guild.leave()
            except discord.NotFound:
                return


async def setup(bot: Red):
    bot.add_cog(GlobalBan(bot))
