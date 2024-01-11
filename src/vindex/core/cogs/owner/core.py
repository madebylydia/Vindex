import typing

import discord
from discord.ext import commands

from vindex.core.i18n import Translator
from vindex.core.ui.formatting import block, inline
from vindex.core.ui.prompt import ConfirmView

if typing.TYPE_CHECKING:
    from vindex.core.bot import Vindex
    from vindex.core.core_types import Context


_ = Translator("Owner", __file__)


class Owner(commands.Cog):
    """Commands reserved for the owner.
    Used for bot's administration & management.
    """

    last_loaded_cog: str | None = None

    def __init__(self, bot: "Vindex") -> None:
        self.bot = bot
        self.last_loaded_cog = None
        super().__init__()

    @commands.is_owner()
    @commands.group(name="owner")
    async def cmd_owner(self, ctx: "Context"):
        """Commands reserved for the owner.
        Used for bot's administration & management.
        """
        # if not ctx.invoked_subcommand:
        #     await ctx.send_help(ctx.command)

    @cmd_owner.group(name="authorization")
    async def cmd_owner_authorization(self, ctx: "Context"):
        """Allow a guild to use the bot."""
        # if not ctx.invoked_subcommand:
        #     await ctx.send_help(ctx.command)

    @cmd_owner_authorization.command(name="allow")
    async def cmd_owner_authorization_allow(self, ctx: "Context", guild_id: int):
        """Allow a guild to use the bot."""
        await self.bot.services.authorization.allow(guild_id)
        await ctx.send(_("This guild has been authorized."))

    @cmd_owner_authorization.command(name="disallow")
    async def cmd_owner_authorization_disallow(self, ctx: "Context", guild_id: int):
        """Disallow a guild to use the bot."""
        await self.bot.services.authorization.disallow(guild_id)
        await ctx.send(_("This guild has been unauthorized."))

    @cmd_owner_authorization.command(name="check")
    async def cmd_owner_authorization_check(self, ctx: "Context", guild_id: int):
        """Check if a guild is allowed to use the bot."""
        is_authorized = await self.bot.services.authorization.is_allowed(guild_id)
        await ctx.send(
            _("This guild has been authorized.")
            if is_authorized
            else _("This guid has not been authorized.")
        )

    @cmd_owner.command(name="notifychannel")
    async def cmd_owner_setchannel(
        self, ctx: "Context", channel: discord.TextChannel | None = None
    ):
        """Set the channel where the bot will send import notification to."""
        if channel is None:
            core = await ctx.db.core.find_unique_or_raise(where={"id": 1})
            if core.notifyChannel is None:
                await ctx.send(_("No notification channel have been set yet."))
                return

            set_channel = self.bot.get_channel(core.notifyChannel)
            assert isinstance(set_channel, discord.TextChannel)
            await ctx.send(
                _("The current channel is {channel}.").format(channel=set_channel.mention)
            )
            return

        await ctx.db.core.update(where={"id": 1}, data={"notifyChannel": channel.id})
        await ctx.send(_("The channel has been set to {channel}.").format(channel=channel.mention))

    @commands.command(name="load")
    async def cmd_owner_load(self, ctx: "Context", cog: str):
        """Load a cog."""
        try:
            await self.bot.services.cogs_manager.load(cog)
            await ctx.send(_("{cog} has been loaded.").format(cog=inline(cog)))
        except Exception as exception:
            exception_block = block(str(exception), "py")
            await ctx.send(_("An error occured:\n{error}").format(error=exception_block))

    @commands.command(name="reload")
    async def cmd_owner_reload(self, ctx: "Context", cog: str | None = None):
        """Reload a cog."""
        if not cog:
            if not self.last_loaded_cog:
                await ctx.send(_("You must specify a cog to reload."))
                return
            cog = self.last_loaded_cog
        try:
            await self.bot.services.cogs_manager.reload(cog)
            await ctx.send(_("{cog} has been reloaded.").format(cog=inline(cog)))
            self.last_loaded_cog = cog
        except Exception as exception:
            exception_block = block(str(exception), "py")
            await ctx.send(_("An error occured:\n{error}").format(error=exception_block))

    @commands.command(name="unload")
    async def cmd_owner_unload(self, ctx: "Context", cog: str):
        """Unload a cog."""
        try:
            await self.bot.services.cogs_manager.unload(cog)
            await ctx.send(_("{cog} has been unloaded.").format(cog=inline(cog)))
        except Exception as exception:
            exception_block = block(str(exception), "py")
            await ctx.send(_("An error occured:\n{error}").format(error=exception_block))

    @commands.command(name="cogs")
    async def cmd_owner_cogs(self, ctx: "Context"):
        """List loaded cogs."""
        cogs = self.bot.extensions

        embed = discord.Embed(
            title=_("Loaded Cogs ({count})").format(count=len(cogs)), color=ctx.color
        )
        embed.description = ", ".join([inline(cog) for cog in cogs])

        await ctx.send(embed=embed)

        async with ctx.typing():
            unloaded = await ctx.db.externalcog.find_many(where={"loaded": False})
            embed = discord.Embed(
                title=_("Known unloaded cogs ({count})").format(count=len(unloaded)),
                color=ctx.color,
            )
            embed.description = ", ".join([inline(cog.path) for cog in unloaded])
            await ctx.send(embed=embed)

    @cmd_owner.command(name="sync")
    async def cmd_owner_sync(self, ctx: "Context", guild: discord.Guild | None = None):
        """Sync the command tree for a guild or globally."""
        if guild is None:
            view = ConfirmView(
                ctx, content=_("Are you sure you want to synchronise the whole tree globally?")
            )
            async with view as confirmed:
                if confirmed is None:
                    return
                if confirmed is False:
                    await ctx.send(_("The command tree has not been synced."))
                    return

        await ctx.bot.tree.sync(guild=guild)
        await ctx.send(
            _("The command tree has been synced.")
            if not guild
            else _("The command tree has been synced for {guild}.").format(
                guild=inline(guild.name)
            )
        )
