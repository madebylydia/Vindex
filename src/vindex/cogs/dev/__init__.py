import typing

from .core import Dev

if typing.TYPE_CHECKING:
    from vindex.core.bot import Vindex


async def setup(bot: "Vindex"):
    cog = Dev(bot)
    await bot.add_cog(cog)
