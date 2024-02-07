import typing


if typing.TYPE_CHECKING:
    from vindex.core.core_types import Context


async def handle_group(ctx: "Context"):
    if not ctx.subcommand_passed:
        return await ctx.send_help(ctx.command)
