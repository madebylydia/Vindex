import logging
import discord
from discord.ext import commands

from prisma import Prisma

from vindex.core.creator.model import Creator

_log = logging.getLogger(__name__)


class Vindex(commands.AutoShardedBot):
    creator: Creator
    """
    The Creator used to create the bot instance.
    """
    
    database: Prisma
    """
    The database linked to the bot instance.
    Connected once the bot is ready. (During ``setup_hook``)
    """

    def __init__(
        self,
        creator: Creator
    ) -> None:
        super().__init__(
            creator.prefix,
            description="Vindex - A DCS helper",
            intents=discord.Intents.all(),
        )
        self.creator = creator
        self.database = Prisma(datasource={
            "url": f"postgresql://{creator.database_user}:{creator.database_password}@{creator.database_host}:5432/{creator.database_name}",
        })

    async def setup_hook(self) -> None:
        _log.info("Connecting to database...")
        await self.database.connect()
        _log.info("Connected to database.")
