import argparse
import asyncio
import logging
import logging.handlers
import subprocess
import sys

import dotenv
import platformdirs
import rich
import uvloop
from rich.logging import RichHandler

from vindex import __version__
from vindex.settings import read_settings

_log = logging.getLogger(__name__)


class VindexNamespace(argparse.Namespace):
    """Arguments that can be passed to Vindex."""

    version: bool
    disable_rich: bool
    log_level: int
    prisma_generate: bool
    prisma_migrate: bool


def run_command(command: str) -> None:
    """Run a provided command in the current shell by creating a new process."""
    with subprocess.Popen(command, shell=True) as process:
        process.wait()


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
        "--prisma-generate",
        action="store_true",
        help="Generate the Prisma client.",
    )
    parser.add_argument(
        "--prisma-migrate",
        action="store_true",
        help="Attempt to migrate the database.",
    )
    return parser.parse_args(sys.argv[1:], namespace=VindexNamespace())


def main():
    """Start Vindex."""
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

    if __debug__:
        _log.info("Loading .env environment variables...")
        dotenv.load_dotenv(dotenv.find_dotenv())

    settings = read_settings()

    async def async_start():
        # The Vindex class should only be imported here.
        # This is due to Prisma imports. It will fail if the Prisma client is not
        # generated first, which can be done with the CLI argument.
        from vindex.core.bot import Vindex

        vindex = Vindex(settings)
        try:
            async with vindex as bot:
                await bot.start(settings.token)
        finally:
            _log.warning("Bot terminated. Disconnecting from database...")
            await vindex.database.disconnect()

    if arguments.prisma_generate:
        run_command("prisma generate")
    if arguments.prisma_migrate:
        run_command("prisma migrate deploy")

    try:
        uvloop.run(async_start())
    except asyncio.exceptions.CancelledError:
        pass


if __name__ == "__main__":
    main()
