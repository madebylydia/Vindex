import typing

from discord.ext import commands

if typing.TYPE_CHECKING:
    from vindex.core.bot import Vindex
    from vindex.core.core_types import Context


class Owner(commands.Cog):
    """Owner related commands."""

    def __init__(self, bot: "Vindex") -> None:
        self.bot = bot
        super().__init__()

    @commands.is_owner()
    @commands.group(name="authorization")
    async def cmd_owner(self, ctx: "Context"):
        """Allow a guild to use the bot."""
        if not ctx.invoked_subcommand:
            await ctx.send_help(ctx.command)

    @cmd_owner.command(name="allow")
    async def cmd_owner_allow(self, ctx: "Context", guild_id: int):
        """Allow a guild to use the bot."""
        await self.bot.services.authorization.allow(guild_id)
        await ctx.send("This guild has been authorized.")

    @cmd_owner.command(name="disallow")
    async def cmd_owner_disallow(self, ctx: "Context", guild_id: int):
        """Disallow a guild to use the bot."""
        await self.bot.services.authorization.disallow(guild_id)
        await ctx.send("This guild has been unauthorized.")

    @cmd_owner.command(name="check")
    async def cmd_owner_check(self, ctx: "Context", guild_id: int):
        """Check if a guild is allowed to use the bot."""
        is_authorized = await self.bot.services.authorization.is_allowed(guild_id)
        await ctx.send(
            "This guild has been authorized."
            if is_authorized
            else "This guid has not been authorized."
        )
