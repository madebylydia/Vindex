import typing

from discord.ext import commands

from vindex.core.core_types import GuildContext
from vindex.core.i18n import Translator
from vindex.core.ui import inline

if typing.TYPE_CHECKING:
    from vindex.core.bot import Vindex

_ = Translator("ServerSettings", __file__)


class ServerSettings(commands.Cog):
    """Server settings related module."""

    bot: "Vindex"

    def __init__(self, bot: "Vindex") -> None:
        self.bot = bot
        super().__init__()

    @commands.group()
    @commands.guild_only()
    @commands.is_owner()
    async def set(self, ctx: GuildContext):
        """Set server settings."""

    @commands.guild_only()
    @set.command()
    async def locale(self, ctx: GuildContext, locale: str | None = None):
        """Get or set the locale for the server."""
        if locale is None:
            locale = await self.bot.services.i18n.get_guild_locale(ctx.guild.id)
            await ctx.send(_(f"The locale for this server is {inline(locale)}."))
            return
        await self.bot.services.i18n.set_guild_locale(ctx.guild.id, locale)
        await ctx.send(_(f"Locale set to {inline(locale)}."))


async def setup(bot: "Vindex"):
    cog = ServerSettings(bot)
    await bot.add_cog(cog)
