import typing

from vindex.core.cogs.admin.core import Admin

if typing.TYPE_CHECKING:
    from vindex.core.bot import Vindex


async def setup(bot: "Vindex"):
    cog = Admin(bot)
    await bot.add_cog(cog)
