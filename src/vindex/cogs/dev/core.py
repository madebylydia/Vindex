import typing

from discord.ext import commands

from vindex.core.core_types import Context
from vindex.core.i18n import Translator

if typing.TYPE_CHECKING:
    from vindex.core.bot import Vindex

_ = Translator("Dev", __file__)


class Dev(commands.Cog):
    """Development related module."""

    bot: "Vindex"

    def __init__(self, bot: "Vindex") -> None:
        self.bot = bot
        super().__init__()

    @commands.command()
    async def ping(self, ctx: Context):
        """Ping! Pong! Have some fun!"""
        await ctx.send(_("Pong!"))

    @commands.is_owner()
    @commands.group("dev", aliases=["d"])
    async def cmd_dev(self, ctx: Context):
        """Development related commands.
        Only available to the owner.
        """

    @cmd_dev.group("orphan")
    async def cmd_dev_orphan(self, ctx: Context):
        """Analyze orphans objects."""

    @cmd_dev_orphan.command("guilds")
    async def cmd_dev_orphan_guilds(self, ctx: Context):
        """List all orphans guilds."""
        # An orphan guild is a guild that is not registered inside the database
        # but the bot is still in it.
        all_guilds = {guild.id: guild for guild in self.bot.guilds}

        registered_guilds = await self.bot.database.guild.find_many(
            where={"id": {"in": list(all_guilds.keys())}}
        )

        registered_guilds_ids = [guild.id for guild in registered_guilds]
        orphan_guilds = [
            guild for guild in all_guilds.values() if guild.id not in registered_guilds_ids
        ]

        if orphan_guilds:
            await ctx.send(
                f"{len(orphan_guilds)} orphan guilds found:\n"
                "\n".join(f"{guild.id} - {guild.name}" for guild in orphan_guilds)
            )
        else:
            await ctx.send("No orphan guild found. Good.")
