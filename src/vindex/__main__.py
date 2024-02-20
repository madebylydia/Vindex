# pylint: disable=protected-access

import argparse
import asyncio
import functools
import logging
import logging.handlers
import os
import signal
import subprocess
import sys
import typing
from datetime import timedelta
from signal import Signals

import dotenv
import platformdirs
import uvloop
from rich.logging import RichHandler

from vindex import __version__
from vindex.settings import read_settings

if typing.TYPE_CHECKING:
    from prisma.client import Client as PrismaClient
    from vindex.core.bot import Vindex

_log = logging.getLogger(__name__)


class VindexNamespace(argparse.Namespace):
    """Arguments that can be passed to Vindex when calling the Vindex module."""

    version: bool
    disable_rich: bool
    log_level: int
    prisma_generate: bool
    prisma_push: bool
    prisma_migrate: bool


class EnvOptions:
    """Options that can be set in the environment to control Vindex."""

    log_level: int
    prisma_generate: bool
    prisma_push: bool
    prisma_migrate: bool

    def __init__(self) -> None:
        self.log_level = int(os.environ.get("VINDEX_LOG_LEVEL", 20))
        self.prisma_generate = bool(int(os.environ.get("VINDEX_PRISMA_GENERATE", 0)))
        self.prisma_push = bool(int(os.environ.get("VINDEX_PRISMA_PUSH", 0)))
        self.prisma_migrate = bool(int(os.environ.get("VINDEX_PRISMA_MIGRATE", 0)))


def run_command(command: str) -> int:
    """Run a provided command in the current shell by creating a new process."""
    with subprocess.Popen(command, shell=True) as process:
        return process.wait()


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
        "--prisma-push",
        action="store_true",
        help=(
            "Push the latest schema to the database. WARNING, this should only be used for "
            "development purposes, NOT FOR PRODUCTION! Use --prisma-migrate instead."
        ),
    )
    parser.add_argument(
        "--prisma-migrate",
        action="store_true",
        help="Attempt to migrate the database. Use --prisma-push for development.",
    )
    return parser.parse_args(sys.argv[1:], namespace=VindexNamespace())


def setup_logging(disable_rich: bool, log_level: int) -> None:
    logging.basicConfig(
        datefmt="%H:%M:%S",
        format="%(name)s (%(funcName)s) : %(message)s",
        handlers=[RichHandler(level=log_level)] if not disable_rich else [],
        level=log_level,
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
        logging.getLogger(logger).setLevel(logging.DEBUG if log_level <= 0 else logging.WARNING)


async def shutdown_handler(bot: "Vindex", received_signal: Signals | None = None) -> None:
    """Handle the shutdown of the bot."""
    if received_signal:
        bot._shutdown = received_signal.value  # pyright: ignore[reportPrivateUsage]
        _log.warning("Received %s. Shutting down...", received_signal.name)
    else:
        _log.warning("Shutting down...")

    try:
        await bot.database.disconnect()
        _log.info("Disconnected from database.")
        await asyncio.wait_for(bot.close(), timeout=10)
        _log.debug("WebSocket closed.")
    finally:
        all_tasks = [
            task for task in asyncio.all_tasks() if task is not asyncio.current_task()
        ]  # Copilot saved me from craziness, I think.
        try:
            for task in all_tasks:
                task.cancel()
            await asyncio.wait_for(asyncio.gather(*all_tasks, return_exceptions=True), timeout=10)
        except asyncio.TimeoutError:
            _log.error(
                (
                    "Failed to cancel all tasks in time! %s out of %s tasks are still running "
                    "wild and free."
                ),
                len([t for t in all_tasks if not t.cancelled()]),
                len(all_tasks),
            )
        sys.exit(bot._shutdown or 1)  # pyright: ignore[reportPrivateUsage]


def global_exception_handler(
    _: "Vindex", __: asyncio.AbstractEventLoop, context: dict[str, typing.Any]
):
    """Handle unhandled exceptions."""
    exception = context.get("exception")
    if exception is not None and isinstance(exception, (SystemExit, KeyboardInterrupt)):
        return
    _log.critical("An unhandled exception occurred in %s:.", exc_info=exception)


def exception_handler(bot: "Vindex", task: asyncio.Future[None]):
    try:
        task.result()
    except (SystemExit, KeyboardInterrupt, asyncio.CancelledError):
        pass
    except Exception as exception:  # pylint: disable=broad-exception-caught
        _log.critical("An unhandled exception occurred.", exc_info=exception)
        _log.critical("Jester really gotta take a shit man. Dying as gracefully as possible.")
        asyncio.create_task(shutdown_handler(bot))


def setup_handling(bot: "Vindex", loop: asyncio.AbstractEventLoop):
    partial = functools.partial(global_exception_handler, bot)
    loop.set_exception_handler(partial)

    # Not all signals will be present.
    signals = [signal.SIGINT, signal.SIGTERM]
    if sys.platform != "win32":
        signals.append(signal.SIGHUP)

    for sent_signal in signals:
        loop.add_signal_handler(
            sent_signal, lambda s=sent_signal: loop.create_task(shutdown_handler(bot, s))
        )


async def init_prisma(url: str) -> "PrismaClient":
    """Create, register and return a new initialized and connected Prisma client."""
    from prisma import Client, register  # pylint: disable=import-outside-toplevel
    from prisma.engine.errors import (  # pylint: disable=import-outside-toplevel
        EngineConnectionError,
    )

    try:
        db = Client(datasource={"url": url})
        await db.connect(timeout=timedelta(seconds=10))
        register(db)
        _log.debug("DB has been registered.")
        return db
    except EngineConnectionError:
        _log.error("Failed to connect to the database. Exiting...", exc_info=True)
        sys.exit(1)


def main():
    """Start Vindex.

    A few logics have been taken from RedBot's __main__.py file. Thank you, Cog-Creators.
    https://github.com/Cog-Creators/Red-DiscordBot/blob/V3/develop/redbot/__main__.py
    """
    bot = None  # For sys.exit at last line, if necessary
    arguments = parse_arguments()

    try:
        env_args = EnvOptions()
    except ValueError:
        _log.error(
            '[red]One of the "VINDEX_PRISMA_*" environment variable is invalid. Please use '
            '"0" for "False" and "1" for "True" only.'
        )
        _log.error("Exiting...")
        sys.exit(1)

    setup_logging(arguments.disable_rich, env_args.log_level or arguments.log_level)

    if __debug__:
        _log.info("Loading .env environment variables...")
        dotenv.load_dotenv(dotenv.find_dotenv())

    try:
        settings = read_settings()
    except KeyError as exception:
        _log.error("Missing environment variable: %s", exception)
        sys.exit(1)

    # Used by Prisma
    os.environ["VINDEX_DB_URL"] = settings.database_url

    if arguments.prisma_generate or env_args.prisma_generate:
        run_command("prisma generate")
    if arguments.prisma_push or env_args.prisma_push:
        run_command("prisma db push")
    if arguments.prisma_migrate or env_args.prisma_migrate:
        run_command("prisma migrate deploy")

    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)

    db = loop.run_until_complete(init_prisma(settings.database_url))

    # Vindex should only imported now, after Prisma has been generated.
    # Otherwise, the Prisma client will try to be imported, and we might risk an exception.
    from vindex.core.bot import Vindex  # pylint: disable=import-outside-toplevel

    bot = Vindex(settings=settings, prisma_client=db)

    setup_handling(bot, loop)

    future = loop.create_task(bot.start(settings.token))
    future.add_done_callback(functools.partial(exception_handler, bot))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.create_task(shutdown_handler(bot, signal.Signals.SIGINT))
    finally:
        _log.debug("Cleaning up...")
        loop.run_until_complete(loop.shutdown_asyncgens())
        if db.is_connected():
            _log.warning("Database was not disconnected! (bad!!!) Doing it now...")
            loop.run_until_complete(db.disconnect())
        asyncio.set_event_loop(None)
        loop.stop()
        loop.close()
        _log.debug("Loop has been closed.")
    sys.exit(bot._shutdown if bot else 1)  # pyright: ignore[reportPrivateUsage]


if __name__ == "__main__":
    main()
