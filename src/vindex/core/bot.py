import logging
import typing
from datetime import datetime

import discord
import rich
from discord.ext import commands
from rich.box import MINIMAL
from rich.columns import Columns
from rich.panel import Panel
from rich.table import Table

from prisma import Prisma
from vindex import __version__ as vindex_version
from vindex.core import extensions
from vindex.core.i18n import set_language_from_guild
from vindex.core.services.provider import ServiceProvider

if typing.TYPE_CHECKING:
    from vindex.core.creator.model import Creator

_log = logging.getLogger(__name__)


VINDEX_HEADER = """[blue]
                               ;
                               ED.
                L.             E#Wi                 ,;
            t   EW:        ,ft E###G.             f#i
            Ej  E##;       t#E E#fD#W;          .E#t
 t      .DD.E#, E###t      t#E E#t t##L        i#W,   :KW,      L
 EK:   ,WK. E#t E#fE#f     t#E E#t  .E#K,     L#D.     ,#W:   ,KG
 E#t  i#D   E#t E#t D#G    t#E E#t    j##f  :K#Wfff;    ;#W. jWi
 E#t j#f    E#t E#t  f#E.  t#E E#t    :E#K: i##WLLLLt    i#KED.
 E#tL#i     E#t E#t   t#K: t#E E#t   t##L    .E#L         L#W.
 E#WW,      E#t E#t    ;#W,t#E E#t .D#W;       f#E:     .GKj#K.
 E#K:       E#t E#t     :K#D#E E#tiW#G.         ,WW;   iWf  i#K.
 ED.        E#t E#t      .E##E E#K##i            .D#; LK:    t#E
 t          E#t ..         G#E E##D.               tt i       tDj
            ,;.             fE E#t
                             , L:
"""
COGS = ("dev",)


class Vindex(extensions.Events):
    """Vindex: Discord Bot made for DCS communities

    This class is the main bot class, the "core" itself;
    """

    def __init__(self, creator: "Creator") -> None:
        self.creator = creator
        self.database = Prisma(datasource={"url": self.creator.build_db_url()})
        super(commands.AutoShardedBot, self).__init__(
            creator.prefix,
            description="Vindex - A DCS helper",
            intents=discord.Intents.all(),
        )
        self.services = ServiceProvider(self)

    async def setup_hook(self) -> None:
        # Database stuff
        await self.database.connect()
        _log.info("Connected to database.")

        # Core cogs
        cogs = ("server_settings",)
        for cog in cogs:
            _log.debug("Loading extension %s", cog)
            await self.load_extension(f"vindex.core.cogs.{cog}")

        # Jishaku cog
        await self.load_extension("jishaku")

        timer_start = datetime.now()
        await self.services.prepare()
        timer_end = datetime.now()
        _log.debug("Services took %s to prepare.", timer_end - timer_start)

        # Load non-core cogs
        for cog in COGS:
            _log.debug("Loading extension %s", cog)
            await self.load_extension(f"vindex.cogs.{cog}")

        _log.info("Done setting up Vindex.")
        await super().setup_hook()

    async def on_guild_join(self, guild: discord.Guild):
        await self.database.guild.create(
            {
                "id": guild.id,
                # TODO: this might create issues, it's not using the expected format IMO
                "locale": guild.preferred_locale.value,
            }
        )

    async def on_ready(self) -> None:
        console = rich.get_console()
        console.print(VINDEX_HEADER)

        settings_table = Table(show_footer=False, show_edge=False, show_header=False, box=MINIMAL)
        settings_table.add_row("Prefix", f"[red]{self.command_prefix}")
        settings_table.add_row("Version", f"[red]{vindex_version}")
        settings_table.add_row("d.py version", f"[red]{discord.__version__}")
        settings_panel = Panel(settings_table, expand=False, title="Settings")

        stats_table = Table(show_footer=False, show_edge=False, show_header=False, box=MINIMAL)
        stats_table.add_row("Guilds", f"[red]{len(self.guilds)}")
        stats_table.add_row("Users", f"[red]{len(self.users)}")
        stats_table.add_row("Shards", f"[red]{self.shard_count}")
        stats_panel = Panel(stats_table, expand=False, title="Stats")

        console.print(Columns((settings_panel, stats_panel)))

    async def on_message(self, message: discord.Message, /) -> None:
        await set_language_from_guild(self, message.guild.id if message.guild else None)
        return await super().on_message(message)
