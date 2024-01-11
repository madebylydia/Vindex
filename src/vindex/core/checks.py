import typing

from discord.ext import commands

if typing.TYPE_CHECKING:
    from vindex.core.core_types import Context


def is_bot_mod():
    async def predicate(ctx: "Context"):
        return await ctx.bot.is_bot_mod(ctx.author)

    return commands.check(predicate)
