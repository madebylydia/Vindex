import typing

from .core import Falx

if typing.TYPE_CHECKING:
    from vindex.core.bot import Vindex


async def setup(bot: "Vindex"):
    cog = Falx(bot)
    await bot.add_cog(cog)
