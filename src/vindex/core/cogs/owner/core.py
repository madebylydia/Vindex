import typing

import discord
from discord.ext import commands

from vindex.core.i18n import Translator
from vindex.core.ui.formatting import block, inline

if typing.TYPE_CHECKING:
    from vindex.core.bot import Vindex
    from vindex.core.core_types import Context


_ = Translator("Owner", __file__)


class Owner(commands.Cog):
    """Commands reserved for the owner.
    Used for bot's administration & management.
    """

    def __init__(self, bot: "Vindex") -> None:
        self.bot = bot
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

    @cmd_owner_authorization.command(name="setchannel")
    async def cmd_owner_setchannel(self, ctx: "Context", channel: discord.TextChannel):
        """Set the channel where the bot will send import notification to."""
        await ctx.db.core.update(where={"id": 1}, data={"notifyChannel": channel.id})
        await ctx.send(_("The channel has been set to {channel}.").format(channel=channel.mention))

    @cmd_owner.command(name="load")
    async def cmd_owner_load(self, ctx: "Context", cog: str):
        """Load a cog."""
        try:
            await self.bot.services.cogs_manager.load(cog)
            await ctx.send(_("{cog} has been loaded.").format(cog=inline(cog)))
        except Exception as exception:
            exception_block = block(str(exception), "py")
            await ctx.send(_("An error occured:\n{error}").format(error=exception_block))

    @cmd_owner.command(name="reload")
    async def cmd_owner_reload(self, ctx: "Context", cog: str):
        """Reload a cog."""
        try:
            await self.bot.services.cogs_manager.reload(cog)
            await ctx.send(_("{cog} has been reloaded.").format(cog=inline(cog)))
        except Exception as exception:
            exception_block = block(str(exception), "py")
            await ctx.send(_("An error occured:\n{error}").format(error=exception_block))

    @cmd_owner.command(name="unload")
    async def cmd_owner_unload(self, ctx: "Context", cog: str):
        """Unoad a cog."""
        try:
            await self.bot.services.cogs_manager.unload(cog)
            await ctx.send(_("{cog} has been unloaded.").format(cog=inline(cog)))
        except Exception as exception:
            exception_block = block(str(exception), "py")
            await ctx.send(_("An error occured:\n{error}").format(error=exception_block))
