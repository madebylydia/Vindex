import argparse
import asyncio
import logging
import logging.handlers
import sys

import dotenv
import platformdirs
import rich
import uvloop
from rich.logging import RichHandler

from vindex import __version__
from vindex.core.bot import Vindex
from vindex.settings import read_settings

_log = logging.getLogger(__name__)


class VindexNamespace(argparse.Namespace):
    """Arguments that can be passed to Vindex."""

    version: bool
    disable_rich: bool
    log_level: int


def parse_arguments() -> VindexNamespace:
    parser = argparse.ArgumentParser(
        prog="Vindex", description="A Discord bot made for DCS communities."
    )
    parser.add_argument("--version", "-v", action="version", version="%(prog)s v" + __version__)
    parser.add_argument(
        "--disable-rich", action="store_true", help="Disable rich as the log handler."
    )
    parser.add_argument(
        "--log-level",
        type=int,
        default=20,
        choices=range(0, 50),
        metavar="[0-50]",
        help="Set the log level. Defaults to INFO (20).",
    )
    parser.add_argument(
        "--ignore-guild-whitelist",
        action="store_true",
        help=(
            "Ignore the guild whitelist and allow the bot to join any guild. Useful for "
            "development purposes."
        ),
    )
    return parser.parse_args(sys.argv[1:], namespace=VindexNamespace())


def main():
    """Start Vindex."""
    if __debug__:
        dotenv.load_dotenv()

    arguments = parse_arguments()

    logging.basicConfig(
        datefmt="%H:%M:%S",
        format="%(name)s (%(funcName)s) : %(message)s",
        handlers=[RichHandler(level=arguments.log_level)] if not arguments.disable_rich else [],
        level=arguments.log_level,
    )
    logging.getLogger("vindex").addHandler(
        logging.handlers.RotatingFileHandler(
            platformdirs.user_log_path("vindex", ensure_exists=True)
            .joinpath("vindex.log")
            .resolve(),
            maxBytes=8**7,
            backupCount=10,
        )
    )
    for logger in ("discord", "prisma", "httpcore", "httpx"):
        logging.getLogger(logger).setLevel(
            logging.DEBUG if arguments.log_level <= 0 else logging.WARNING
        )

    console = rich.get_console()

    console.print("[yellow]Starting engine, stand by...[/]")

    settings = read_settings()

    async def async_start():
        vindex = Vindex(settings)
        try:
            async with vindex as bot:
                await bot.start(settings.token)
        finally:
            _log.warning("Bot terminated. Disconnecting from database...")
            await vindex.database.disconnect()

    try:
        uvloop.run(async_start())
    except asyncio.exceptions.CancelledError:
        pass


if __name__ == "__main__":
    main()
