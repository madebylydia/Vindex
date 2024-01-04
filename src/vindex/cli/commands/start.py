import logging
import os
import sys

import click
import rich
import uvloop
from rich.logging import RichHandler

from vindex.core.bot import Vindex
from vindex.core.creator.reader import fetch_creator
from vindex.core.exceptions.invalid_creator import CreatorException

_log = logging.getLogger(__name__)


@click.command()
@click.argument("name", required=True)
@click.option("--log-level", type=click.IntRange(0, 50), default=30)
def start(name: str, log_level: int):
    """Start Vindex."""
    os.environ["PYTHONOPTIMIZE"] = "1"

    logging.basicConfig(
        datefmt="%H:%M:%S",
        format="%(name)s (%(funcName)s) : %(message)s",
        handlers=[RichHandler(level=log_level)],
        level=log_level,
    )
    for logger in ("discord", "prisma", "httpcore", "httpx"):
        logging.getLogger(logger).setLevel(logging.DEBUG if log_level <= 0 else logging.WARNING)

    console = rich.get_console()

    console.print("[yellow]Starting engine, stand by...[/]")

    try:
        creator = fetch_creator()
    except CreatorException:
        console.print(
            "[red]It appears that you have not setup Vindex. Please run [blue]vindex setup[/blue] "
            "to setup Vindex first."
        )
        sys.exit(1)

    instance = creator.instances.get(name)
    if not instance:
        console.print(
            f"[red]It appears that you do not have an instance called [blue]{name}[/blue]. "
            f"Please run [blue]vindex setup {name}[/blue] to setup this instance."
        )
        sys.exit(1)

    async def async_start():
        vindex = Vindex(instance)
        try:
            async with vindex as bot:
                await bot.start(instance.token)
        finally:
            _log.warning("Bot terminated. Disconnecting from database...")
            await vindex.database.disconnect()

    uvloop.run(async_start())
