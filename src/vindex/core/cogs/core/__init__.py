import typing

from .corecmd import Core

if typing.TYPE_CHECKING:
    from vindex.core.bot import Vindex


async def setup(bot: "Vindex"):
    cog = Core(bot)
    await bot.add_cog(cog)
