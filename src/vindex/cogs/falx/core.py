import logging
import typing

import discord
from discord.ext import commands

from prisma.models import GuildAllowance
from vindex.core.checks import is_bot_mod
from vindex.core.i18n import Translator
from vindex.core.utils import AsyncIterator
from vindex.core.utils.prompt import ConfirmView

from .messages import falx_check, falx_join, falx_leave, falx_startup

if typing.TYPE_CHECKING:
    from prisma import Client
    from vindex.core.bot import Vindex
    from vindex.core.core_types import Context


_ = Translator("Falx", __file__)
_log = logging.getLogger(__name__)


class Falx(commands.Cog):
    """The guild authorization layer of Vindex."""

    bot: "Vindex"
    db: "Client"

    def __init__(self, bot: "Vindex") -> None:
        self.bot = bot
        self.db = bot.database
        super().__init__()

    async def is_guild_allowed(self, guild_id: int) -> bool:
        """Indicates if the guild is allowed to use the bot or not.

        This will also return `False` if the guild has no record in the database.
        """
        guild_data = await GuildAllowance.prisma().find_unique(where={"id": str(guild_id)})
        if not guild_data:
            return False
        return guild_data.allowed

    async def is_guild_known(self, guild_id: int) -> bool:
        """Indicates if the guild is known to the the GuildAllowance layer."""
        guild_data = await GuildAllowance.prisma().find_unique(where={"id": str(guild_id)})
        return guild_data is not None

    @commands.group(name="falx")
    @is_bot_mod()
    async def cmd_falx(self, ctx: "Context"):
        """Guild authorization layer of Vindex."""
        if not ctx.subcommand_passed:
            return await ctx.send_help(ctx.command)

    @cmd_falx.command(name="seed")
    async def cmd_falx_seed(self, ctx: "Context"):
        """Seed existing guilds. This will allow all guilds the bot has already joined."""
        async with (ConfirmView(ctx, content=_("Are you sure you want to seed all guilds?"))) as (
            confirmed,
            __,
        ):
            if not confirmed:
                return

        count = 0
        for guild in self.bot.guilds:
            await GuildAllowance.prisma().upsert(
                where={"id": str(guild.id)},
                data={
                    "create": {
                        "id": str(guild.id),
                        "allowed": True,
                        "allowanceReason": f"Automatic seeding of {guild.name} by {ctx.author.id}",
                        "createdById": str(ctx.author.id),
                    },
                    "update": {
                        "allowed": True,
                        "allowanceReason": f"Automatic seeding of {guild.name} by {ctx.author.id}",
                        "createdBy": {"connect": {"id": str(ctx.author.id)}},
                    },
                },
            )
            count += 1

        await ctx.send(_("Done. {count} guilds were succesfully seeded.").format(count=count))

    @cmd_falx.command(name="allow", aliases=["add"])
    async def cmd_falx_allow(
        self, ctx: "Context", guild_or_id: discord.Guild | int, *, reason: str
    ):
        """Allow a guild to use Vindex.

        Parameters
        ----------
        guild_or_id : Guild or integer
            The guild to allow.
        reason : str
            The reason for allowing the guild.
        """
        if len(reason) > 1000:
            await ctx.send(_("The reason must be 1000 characters long or less."))
            return

        guild_id = guild_or_id if isinstance(guild_or_id, int) else guild_or_id.id

        guild_data = await GuildAllowance.prisma().find_first(where={"id": str(guild_id)})
        if guild_data and guild_data.allowed:
            await ctx.send(_("This guild is already allowed."))
            return

        await GuildAllowance.prisma().upsert(
            where={"id": str(guild_id)},
            data={
                "create": {
                    "id": str(guild_id),
                    "allowed": True,
                    "allowanceReason": reason,
                    "createdBy": {
                        "connect": {"id": str(ctx.author.id)},
                        "create": {"id": str(ctx.author.id)},
                    },
                },
                "update": {
                    "allowed": True,
                    "allowanceReason": reason,
                    "createdBy": {
                        "connect": {"id": str(ctx.author.id)},
                        "create": {"id": str(ctx.author.id)},
                    },
                },
            },
        )
        await ctx.send(_("This guild is now allowed."))

    @cmd_falx.command(name="disallow", aliases=["remove"])
    async def cmd_falx_disallow(
        self,
        ctx: "Context",
        guild_or_id: discord.Guild | int,
        *,
        reason: str,
    ):
        """Disallow a guild to use Vindex.

        Parameters
        ----------
        guild_or_id : discord.Guild | int
            The guild to disallow.
        reason : str
            The reason for disallowing the guild.
        """
        if len(reason) > 1000:
            await ctx.send(_("The reason must be 1000 characters long or less."))
            return

        guild_id = guild_or_id if isinstance(guild_or_id, int) else guild_or_id.id

        guild_data = await GuildAllowance.prisma().find_first(where={"id": str(guild_id)})
        if not guild_data or not guild_data.allowed:
            await ctx.send(_("This guild is already disallowed."))
            return

        await GuildAllowance.prisma().upsert(
            where={"id": str(guild_id)},
            data={
                "create": {
                    "id": str(guild_id),
                    "allowed": False,
                    "allowanceReason": reason,
                    "createdBy": {
                        "connect": {"id": str(ctx.author.id)},
                        "create": {"id": str(ctx.author.id)},
                    },
                },
                "update": {
                    "allowed": False,
                    "allowanceReason": reason,
                    "createdBy": {
                        "connect": {"id": str(ctx.author.id)},
                        "create": {"id": str(ctx.author.id)},
                    },
                },
            },
        )

        fetched_guild = self.bot.get_guild(guild_id)
        if fetched_guild:
            async with ConfirmView(
                ctx, content=_("Disallowed. I am still in this guild. Do you wish me to leave it?")
            ) as (confirmed, __):
                if confirmed:
                    await fetched_guild.leave()
        else:
            await ctx.send(_("This guild is now disallowed."))

    @cmd_falx.command(name="forget", aliases=["drop"])
    async def cmd_falx_forget(self, ctx: "Context", guild_or_id: discord.Guild | int):
        """Forget a guild from the database.

        Parameters
        ----------
        guild_or_id : Guild or int
            The guild to forget.
        """
        guild_id = guild_or_id if isinstance(guild_or_id, int) else guild_or_id.id

        record = await GuildAllowance.prisma().delete(where={"id": str(guild_id)})

        if record:
            await ctx.send(_("Record deleted."))
        else:
            await ctx.send(_("No record found."))

    @cmd_falx.command(name="check")
    async def cmd_falx_check(self, ctx: "Context", guild_or_id: discord.Guild | int):
        """Check if a guild is allowed to use Vindex.

        Parameters
        ----------
        guild_or_id : Guild or integer
            The guild to check.
        """
        guild_id = guild_or_id if isinstance(guild_or_id, int) else guild_or_id.id

        record = await GuildAllowance.prisma().find_unique(
            where={"id": str(guild_id)}, include={"createdBy": True}
        )
        if not record:
            await ctx.send(_("No record found."))
            return

        await ctx.send(embed=falx_check(self.bot, record))

    async def cog_load_task(self) -> None:
        """On cog load, this will check for guilds that have been left while the bot bot was
        online, or when the cog was unloaded.
        """
        await self.bot.wait_until_ready()

        unknown_guilds: list[discord.Guild] = []
        is_disallowed: list[discord.Guild] = []

        async for guild in AsyncIterator(self.bot.guilds):
            # I shall thank you Fixator10, for teaching me how to properly use async iterators. :)
            if not await self.is_guild_known(guild.id):
                unknown_guilds.append(guild)
                continue
            if not await self.is_guild_allowed(guild.id):
                is_disallowed.append(guild)

        async for unallowed_guild in AsyncIterator(is_disallowed):
            await unallowed_guild.leave()

        if unknown_guilds or is_disallowed:
            await self.bot.core_notify(embeds=[falx_startup(is_disallowed, unknown_guilds)])

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """Handle guild join events."""
        allowed = await self.is_guild_allowed(guild.id)

        if not guild.chunked:
            await guild.chunk()  # used for members info

        await self.bot.core_notify(embeds=[falx_join(guild, allowed)])
        if not allowed:
            await guild.leave()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        """Handle guild leave events."""
        allowed = await self.is_guild_allowed(guild.id)

        if not allowed:
            # We already sent the on_guild_join embed that is above. No need for the leave embed.
            return

        await GuildAllowance.prisma().update(
            where={"id": str(guild.id)},
            data={
                "allowed": False,
                "allowanceReason": "Guild was left, allowance removed by bot.",
            },
        )

        if not guild.chunked:
            await guild.chunk()  # used for members info

        await self.bot.core_notify(embeds=[falx_leave(guild)])
