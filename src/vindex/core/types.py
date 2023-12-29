import typing

if typing.TYPE_CHECKING:
    from discord.ext import commands

    from vindex.core.bot import Vindex

type Context = "commands.Context[Vindex]"
