import logging

from discord.ext import commands

from vindex.core.core_types import Context
from vindex.core.defintions import ABCVindex

_log = logging.getLogger(__name__)


class Events(ABCVindex):
    """The Events extension of Vindex."""

    async def on_command_error(
        self, context: Context, exception: commands.errors.CommandError, /
    ) -> None:
        _log.exception("An error occured while executing a command.", exc_info=exception)
        if isinstance(exception, commands.errors.CommandNotFound):
            await context.send("Could not find such command.")
            return
        if isinstance(exception, commands.errors.MissingRequiredArgument):
            await context.send_help(context.command)
            return
        return await super().on_command_error(context, exception)
