import typing

from discord.ext import commands

if typing.TYPE_CHECKING:
    from vindex.core.bot import Vindex
    from vindex.core.core_types import Context


class HelpMenu:
    pass


class Meta(commands.Cog):
    """A cog providing (meta) informations about the bot."""

    bot: "Vindex"

    def __init__(self, bot: "Vindex") -> None:
        self.bot = bot
        super().__init__()

    @commands.hybrid_command(name="help")
    async def cmd_help(self, ctx: "Context", *, resource: str | None = None):
        """Request a tanker for emergency refuel. (things like that)"""
        if resource:
            await ctx.send_help(resource)
            return
        await ctx.send("I will send the global help here.")
        await ctx.send_help()
