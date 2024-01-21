import typing

from .core import Meta

if typing.TYPE_CHECKING:
    from vindex.core.bot import Vindex


async def setup(bot: "Vindex"):
    cog = Meta(bot)
    bot.remove_command("help")
    await bot.add_cog(cog)
