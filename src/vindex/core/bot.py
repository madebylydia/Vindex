import logging
import pathlib
import pkgutil
import typing
from contextlib import suppress

import discord
import rich
from discord import app_commands
from discord.app_commands.errors import AppCommandError
from discord.ext import commands
from discord.interactions import Interaction
from rich.box import MINIMAL
from rich.columns import Columns
from rich.panel import Panel
from rich.table import Table

import prisma
from vindex import __version__ as vindex_version
from vindex.core.core_types import Context, SendMethodDict
from vindex.core.i18n import Translator, set_language_from_guild
from vindex.core.services.provider import ServiceProvider

if typing.TYPE_CHECKING:
    from datetime import datetime

    from vindex.settings import Settings

_log = logging.getLogger(__name__)


VINDEX_HEADER = """[blue]
                               ED.
                L.             E#Wi                ,;
            t   EW:        ,ft E###G.             f#i
            Ej  E##;       t#E E#fD#W;          .E#t
t      .DD. E#, E###t      t#E E#t t##L        i#W,   :KW,      L
EK:   ,WK.  E#t E#fE#f     t#E E#t  .E#K,     L#D.     ,#W:   ,KG
E#t  i#D    E#t E#t D#G    t#E E#t    j##f  :K#Wfff;    ;#W. jWi
E#t j#f     E#t E#t  f#E.  t#E E#t    :E#K: i##WLLLLt    i#KED.
E#tL#i      E#t E#t   t#K: t#E E#t   t##L    .E#L         L#W.
E#WW,       E#t E#t    ;#W,t#E E#t .D#W;       f#E:     .GKj#K.
E#K:        E#t E#t     :K#D#E E#tiW#G.         ,WW;   iWf  i#K.
ED.         E#t E#t      .E##E E#K##i            .D#; LK:    t#E
t           E#t ..         G#E E##D.               tt i       tDj
            ,;.             fE E#t
                             , L:
"""


_ = Translator("Vindex", __file__)


def get_intents() -> discord.Intents:
    intents = discord.Intents.default()
    intents.members = True
    return intents


class VindexTree(app_commands.CommandTree["Vindex"]):
    """Internal command tree for Vindex hybrid/app commands."""

    async def on_error(self, interaction: Interaction["Vindex"], error: AppCommandError) -> None:
        _log.error("Error inside the app commands tree", exc_info=True)
        return await super().on_error(interaction, error)


class Vindex(commands.AutoShardedBot):
    """Vindex: Discord Bot made for DCS communities

    This class is the main bot class, the "core" itself;
    """

    uptime: "datetime"

    bot_mods: list[int]

    def __init__(self, settings: "Settings") -> None:
        self.settings = settings
        self.database = prisma.Prisma(datasource={"url": self.settings.database_url})
        super().__init__(
            commands.when_mentioned,
            tree_cls=VindexTree,
            description="Vindex - A DCS helper",
            intents=get_intents(),
            chunk_guilds_at_startup=False,
            allowed_mentions=discord.AllowedMentions(
                everyone=False, roles=False, users=True, replied_user=True
            ),
        )
        self.services = ServiceProvider(self)

        self.add_check(self.check_is_blacklisted)
        self.add_check(self.check_is_chunked_or_chunk)

    @property
    def owner_name(self) -> str | None:
        """Attempt to return the name of the owner of the instance.

        Returns
        -------
        str or None
            The name of the owner of the instance.
            None if the application is not set yet. (Wait for bot to connect)
        """
        if not self.application:
            return None
        if self.application.team:
            return self.application.team.name
        return self.application.owner.name

    async def add_bot_mod(self, user: discord.abc.User, /) -> None:
        """Add a bot moderator.

        Parameters
        ----------
        user: discord.abc.User
            The user to add.
        """
        await self.database.user.upsert(
            where={"id": user.id},
            data={"create": {"id": user.id, "isBotMod": True}, "update": {"isBotMod": True}},
        )
        self.bot_mods.append(user.id)

    async def remove_bot_mod(self, user: discord.abc.User, /) -> None:
        """Remove a bot moderator.

        Parameters
        ----------
        user: discord.abc.User
            The user to remove.
        """
        await self.database.user.upsert(
            where={"id": user.id},
            data={"create": {"id": user.id, "isBotMod": False}, "update": {"isBotMod": False}},
        )
        self.bot_mods.remove(user.id)

    async def is_bot_mod(self, user: discord.abc.User, /) -> bool:
        """Check if a user is a bot moderator.

        Parameters
        ----------
        user: discord.abc.User
            The user to check.

        Returns
        -------
        bool
            Whether the user is a bot moderator or not.
        """
        return await self.is_owner(user) or user.id in self.bot_mods

    async def core_notify(self, **kwargs: typing.Unpack[SendMethodDict]) -> discord.Message | None:
        """Send a message to the core notification channel.
        This should be used to send messages that the owner must be aware of. For example, join of
        a new guild (Since bot works on an authorization system).

        Parameters
        ----------
        **kwargs: The
            Same argument as :py:meth:`discord.abc.Messageable.send`. Typed.

        Returns
        -------
        discord.Message or None
            The message sent. None if no channel were set.
        """
        core = await self.database.core.find_unique_or_raise({"id": 1})
        channel = self.get_channel(core.notifyChannel) if core.notifyChannel else None
        if not channel:
            _log.error(
                "An attempt was made to send a core notification, but no channel was set. Ignoring."
            )
            return None
        assert isinstance(channel, discord.TextChannel)
        return await channel.send(**kwargs)

    @typing.overload
    async def get_or_fetch_user(
        self, user_id: int, /, *, as_none: typing.Literal[False] = False
    ) -> discord.User:
        ...

    @typing.overload
    async def get_or_fetch_user(
        self, user_id: int, /, *, as_none: typing.Literal[True] = True
    ) -> discord.User | None:
        ...

    async def get_or_fetch_user(
        self, user_id: int, /, *, as_none: bool = False
    ) -> discord.User | None:
        """Attempt to get an user from the bot's memory. In case it fails, attempt to fetch it
        instead.

        Parameters
        ----------
        user_id: int
            The user ID to get or fetch.
        as_none: bool
            Whether to return None if the user was not found, or rather raise an exception.
            Defaults to ``False``.

        Raises
        ------
        discord.NotFound
            If the user was not found.

        Returns
        -------
        discord.User
            The user fetched or None if it failed.
        """
        user = self.get_user(user_id)
        if not user:
            try:
                user = await self.fetch_user(user_id)
            except discord.NotFound:
                if as_none:
                    return None
                raise
        return user

    async def get_or_fetch_member(self, guild: discord.Guild, user_id: int, /) -> discord.Member:
        """Attempt to get a member from the bot's memory. In case it fails, attempt to fetch it
        instead.

        Parameters
        ----------
        guild: discord.Guild
            The guild to get the member from.
        user_id: int
            The user ID to get or fetch.

        Raises
        ------
        discord.NotFound
            If the member was not found.

        Returns
        -------
        discord.Member
            The member fetched or None if it failed.
        """
        member = guild.get_member(user_id)
        if not member:
            member = await guild.fetch_member(user_id)
        return member

    async def setup_hook(self) -> None:
        # Database stuff
        await self.database.connect()
        prisma.register(self.database)
        _log.info("Connected to database.")

        # Ensuring there is a Core row existing
        try:
            await self.database.core.find_unique_or_raise({"id": 1})
        except prisma.errors.RecordNotFoundError:
            await self.database.core.create({"id": 1})
        self.bot_mods = [
            user.id for user in await self.database.user.find_many(where={"isBotMod": True})
        ]

        # Core cogs (Most-load cogs)
        modules = pkgutil.iter_modules(
            [str(pathlib.Path(__file__, "..", "cogs").resolve())], prefix="vindex.core.cogs."
        )
        for module in modules:
            if module.name.startswith("_"):
                continue
            await self.load_extension(module.name)

        # Jishaku cog
        await self.load_extension("jishaku")

        timer_start = discord.utils.utcnow()
        await self.services.prepare()
        timer_end = discord.utils.utcnow()
        _log.debug("Services took %s to prepare.", timer_end - timer_start)

        _log.info("Done setting up Vindex.")
        await super().setup_hook()

    async def get_context(
        self, origin: discord.Message | discord.Interaction, /, *, cls: type = Context
    ) -> Context:
        return await super().get_context(origin, cls=cls)

    async def on_command_error(  # pyright: ignore[reportIncompatibleMethodOverride]
        # Weirdest issue I ever had
        self,
        context: Context,
        exception: commands.errors.CommandError,
        /,
    ) -> None:
        if self.extra_events.get("on_command_error", None):
            return
        if context.command and context.command.has_error_handler():
            return
        if context.cog and context.cog.has_error_handler():
            return

        if isinstance(exception, commands.errors.HybridCommandError):
            exception = exception.original  # type: ignore

        if isinstance(exception, commands.errors.NotOwner):
            return
        if isinstance(exception, commands.errors.CommandNotFound):
            await context.send(_("Could not find such command."))
            return
        if isinstance(
            exception, (commands.errors.MissingRequiredArgument, commands.errors.TooManyArguments)
        ):
            await context.send_help(context.command)
            return

        if isinstance(exception, discord.errors.HTTPException):
            with suppress(discord.errors.HTTPException):
                await context.send(
                    _(
                        "An internal error occured. This look like an unhandled error. Feel free to try "
                        "again. If this error keep occuring, please contact the bot owner."
                    )
                )

        await self.core_notify(
            content=(
                "An error occured while executing a command. Please check internal log for "
                "traceback."
            )
        )
        _log.exception(
            "An error occured while executing a command: %s", context.command, exc_info=exception
        )

    async def on_connect(self):
        assert self.user
        activity = discord.CustomActivity(_("Vindex is connecting and setting up..."))
        await self.change_presence(status=discord.Status.idle, activity=activity)
        _log.info("Connected to Discord.")

    async def on_ready(self) -> None:
        assert self.user
        self.uptime = discord.utils.utcnow()

        console = rich.get_console()
        console.print(VINDEX_HEADER)
        console.print(
            _(
                "[cyan]Connected as [green]{me}[/green]. Owned by [green]{owner}[/green].[/]"
            ).format(me=self.user, owner=self.owner_name)
        )

        settings_table = Table(show_footer=False, show_edge=False, show_header=False, box=MINIMAL)
        settings_table.add_row(_("Prefix"), f"[red]<@{self.user.id}>")
        settings_table.add_row(_("Vindex version"), f"[red]{vindex_version}")
        settings_table.add_row(_("Discord.py version"), f"[red]{discord.__version__}")
        settings_panel = Panel(settings_table, expand=False, title="Settings")

        stats_table = Table(show_footer=False, show_edge=False, show_header=False, box=MINIMAL)
        stats_table.add_row(_("Guilds"), f"[red]{len(self.guilds)}")
        stats_table.add_row(_("Users"), f"[red]{len(self.users)}")
        stats_table.add_row(_("Shards"), f"[red]{self.shard_count}")
        stats_panel = Panel(stats_table, expand=False, title="Stats")

        console.print(Columns((settings_panel, stats_panel)))

        await self.change_presence(
            status=discord.Status.online,
            activity=discord.CustomActivity(_("Flying the F-14B Tomcat")),
        )

    # A few global checks

    @staticmethod
    async def check_is_blacklisted(ctx: Context):
        return not ctx.bot.services.blacklist.is_blacklisted(ctx.author.id)

    @staticmethod
    async def check_is_chunked_or_chunk(ctx: Context):
        if not ctx.guild:
            return True
        if not ctx.guild.chunked:
            await ctx.guild.chunk()
        return True

    async def on_message(self, message: discord.Message, /) -> None:
        await set_language_from_guild(self, message.guild.id if message.guild else None)
        return await super().on_message(message)
