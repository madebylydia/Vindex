import asyncio
import logging

import click
import rich
import uvloop
from rich.logging import RichHandler

from vindex.core.bot import Vindex
from vindex.core.creator.reader import fetch_creator
from vindex.core.exceptions.invalid_creator import CreatorException

_log = logging.getLogger(__name__)


@click.command()
@click.option("--log-level", type=click.IntRange(0, 50), default=30)
def start(log_level: int):
    """
    Start Vindex.
    """
    logging.basicConfig(
        datefmt="%H:%M:%S",
        format="%(name)s (%(funcName)s) : %(message)s",
        handlers=[RichHandler(level=log_level)],
        level=log_level,
    )

    console = rich.get_console()

    console.print("[yellow]Starting engine, stand by...[/]")

    try:
        creator = fetch_creator()
    except CreatorException:
        console.print(
            "[red]It appears that you have not setup Vindex. Please run [blue]vindex setup[/blue] to setup Vindex first."
        )
        exit(1)

    async def async_start():
        vindex = Vindex(creator)
        try:
            async with vindex as bot:
                await bot.start(creator.token)
        finally:
            _log.warning("Bot has disconnected. Disconnecting from database...")
            await vindex.database.disconnect()

    asyncio.run(async_start())
