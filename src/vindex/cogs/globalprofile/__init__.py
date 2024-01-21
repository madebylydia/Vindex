import typing

from .core import GlobalProfile

if typing.TYPE_CHECKING:
    from vindex.core.bot import Vindex


async def setup(bot: "Vindex"):
    cog = GlobalProfile(bot)
    await bot.add_cog(cog)
