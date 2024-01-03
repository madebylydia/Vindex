import typing

import discord
from discord.ext import commands

from vindex.core.core_types import Context, GuildContext
from vindex.core.i18n import Languages, Translator
from vindex.core.ui import inline

if typing.TYPE_CHECKING:
    from vindex.core.bot import Vindex

_ = Translator("ServerSettings", __file__)


class Core(commands.Cog):
    """Server settings related module."""

    bot: "Vindex"

    def __init__(self, bot: "Vindex") -> None:
        self.bot = bot
        super().__init__()

    @commands.is_owner()
    @commands.guild_only()
    @commands.group("set")
    async def cmd_set(self, ctx: GuildContext):
        """Set server settings."""

    @cmd_set.command("locale")
    async def cmd_set_locale(self, ctx: GuildContext, locale: Languages | None = None):
        """Get or set the locale for the server."""
        if locale is None:
            guild_locale = await self.bot.services.i18n.get_guild_locale(ctx.guild.id)
            await ctx.send(
                _("The locale for this server is {locale}.").format(
                    locale=inline(guild_locale.value)
                )
            )
            return
        await self.bot.services.i18n.set_guild_locale(ctx.guild.id, locale)
        await ctx.send(_("Locale set to {locale}.").format(locale=inline(locale.value)))

    @commands.is_owner()
    @commands.command("invite")
    async def cmd_invite(self, ctx: Context):
        """Return an invitation code where to invite the bot."""
        assert self.bot.user is not None
        invite_permissions_code = (
            await ctx.db.core.find_unique_or_raise({"id": 1})
        ).invitePermissionCode
        invite_permissions = discord.Permissions(invite_permissions_code or 40544595463233)
        invite_url = discord.utils.oauth_url(
            self.bot.user.id,
            permissions=invite_permissions,
            scopes=(
                "bot",
                "applications.commands",
            ),
        )
        await ctx.send(invite_url)
