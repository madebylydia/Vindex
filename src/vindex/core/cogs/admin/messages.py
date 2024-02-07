import typing

import discord

from vindex.core.i18n import Translator
from vindex.core.ui.formatting import inline

if typing.TYPE_CHECKING:
    from prisma.models import Blacklist

    from vindex.core.core_types import Context


_ = Translator("Admin", __file__)


async def blacklist_add(ctx: "Context", blacklist_entry: "Blacklist") -> discord.Embed:
    embed = discord.Embed(
        title="[Blacklist] Entry added",
        description=_(
            "A new blacklist entry has been added by {author}.\nReason: {reason}"
        ).format(author=inline(str(ctx.author)), reason=blacklist_entry.reason),
        color=discord.Color.dark_red(),
        timestamp=blacklist_entry.createdAt,
    )

    embed.add_field(
        name=_("User ID"),
        value=str(blacklist_entry.id),
    )
    if user := await ctx.bot.get_or_fetch_user(blacklist_entry.id, as_none=True):
        embed.add_field(
            name=_("User information"),
            value=_("Name: {name}\n" "Created at: {created_at}\n").format(
                name=user.display_name, created_at=user.created_at
            ),
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        if user.banner:
            embed.set_image(url=user.banner.url)

    embed.set_footer(text=_("Blacklisted by {author}").format(author=str(ctx.author)))

    return embed


async def blacklist_remove(
    ctx: "Context", removed_blacklist_entry: "Blacklist", reason: str
) -> discord.Embed:
    embed = discord.Embed(
        title="[Blacklist] Entry removed",
        description=_("A blacklist entry has been deleted by {author}.\nReason: {reason}").format(
            author=inline(str(ctx.author)), reason=reason
        ),
        color=discord.Color.dark_green(),
        timestamp=removed_blacklist_entry.createdAt,
    )

    embed.add_field(
        name=_("User ID"),
        value=str(removed_blacklist_entry.id),
    )
    if user := await ctx.bot.get_or_fetch_user(removed_blacklist_entry.id, as_none=True):
        embed.add_field(
            name=_("User information"),
            value=_("Name: {name}\n" "Created at: {created_at}\n").format(
                name=user.display_name, created_at=user.created_at
            ),
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        if user.banner:
            embed.set_image(url=user.banner.url)
    embed.add_field(name="Blacklist reason", value=removed_blacklist_entry.reason)

    embed.set_footer(text=_("Blacklisted by {author}").format(author=str(ctx.author)))

    return embed
