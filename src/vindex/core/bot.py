import logging

import discord
from discord.ext import commands
from discord.message import Message

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

    def __init__(self, creator: Creator) -> None:
        super().__init__(
            creator.prefix,
            description="Vindex - A DCS helper",
            intents=discord.Intents.all(),
        )
        self.creator = creator
        self.database = Prisma(datasource={"url": self.creator.build_db_url()})

    async def setup_hook(self) -> None:
        await self.database.connect()
        await super().setup_hook()

    async def on_ready(self) -> None:
        _log.info("Bot is ready.")

    # async def on_message(self, message: Message) -> None:
    #     print(message)
    #     return await super().on_message(message)
