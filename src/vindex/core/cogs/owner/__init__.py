import typing

from .core import Owner

if typing.TYPE_CHECKING:
    from vindex.core.bot import Vindex


async def setup(bot: "Vindex"):
    cog = Owner(bot)
    await bot.add_cog(cog)
