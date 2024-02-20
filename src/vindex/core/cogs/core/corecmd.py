import typing

import discord
from discord import app_commands
from discord.ext import commands

from vindex import __version__
from vindex.core.i18n import Languages, Translator
from vindex.core.utils.formatting import inline

if typing.TYPE_CHECKING:
    from vindex.core.bot import Vindex
    from vindex.core.core_types import Context, GuildContext

_ = Translator("ServerSettings", __file__)


class Core(commands.Cog):
    """Server settings related module."""

    bot: "Vindex"

    def __init__(self, bot: "Vindex") -> None:
        self.bot = bot
        super().__init__()

    @commands.is_owner()
    @commands.guild_only()
    @commands.hybrid_group("set")
    async def cmd_set(self, ctx: "GuildContext"):
        """Set server settings."""

    @cmd_set.command(
        "locale",
        description=(
            "Get or set the locale of your server. Use no argument to see which language you're "
            "currently using."
        ),
    )
    @app_commands.describe(locale="Language to use for the server.")
    async def cmd_set_locale(self, ctx: "GuildContext", locale: Languages | None = None):
        """Get or set the locale for the server.

        Availables languages are:
        `af` : Afrikaans, `zh` : Chinese, `nl` : Dutch, `en` : English, `fr` : French,
        `de` : German, `it` : Italian, `ja` : Japanese, `no` : Norwegian, `pl` : Polish,
        `ro` : Romanian, `ru` : Russian, `es` : Spanish

        Use the 2-letter code to set the locale.
        """
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

    @commands.hybrid_command("invite")
    async def cmd_invite(self, ctx: "Context"):
        """Return an invitation code where to invite the bot."""
        assert self.bot.user
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
        await ctx.send(
            _("Don't forget to ask for your guild to be whitelisted first.\n{url}").format(
                url=invite_url
            )
        )

    @commands.hybrid_command("about")
    async def cmd_about(self, ctx: "Context"):
        """Return information about the bot."""
        assert self.bot.user
        embed = discord.Embed(
            title=_("About Vindex"),
            description=_(
                "Vindex is a bot made for DCS communities.\nIt is a versatile tool made to help "
                "servers and users in the most redundant tasks.\nWith Vindex, you can create an "
                "universal profile, create events based on your member's modules, and more.\n\n"
                "**Vindex is a work-in-progress.** Most of its features must still be made and "
                "will be once available in a foreseable future.\n\nVindex is an open-source "
                "effort by `lydia39`. The source code is available at [this GitHub repository]"
                "(https://github.com/madebylydia/Vindex).\nI thank you for using Vindex!"
            ),
            color=ctx.color,
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        embed.add_field(name=_("Running Vindex version"), value=f"Vindex v{__version__}")
        embed.add_field(
            name=_("Running discord.py version"), value=f"discord.py v{discord.__version__}"
        )
        embed.add_field(
            name=_("Running Python version"),
            value=f"Python v{__import__('platform').python_version()}",
        )

        owner = ctx.bot.owner_id
        owner_info = ctx.bot.get_user(owner) if owner else None
        if owner_info:
            embed.set_footer(
                text=_("Instance owned by {owner} / dev={dev}").format(
                    owner=owner_info.name, dev=str(__debug__)
                ),
                icon_url=owner_info.display_avatar.url if owner_info else None,
            )

        await ctx.send(embed=embed)
