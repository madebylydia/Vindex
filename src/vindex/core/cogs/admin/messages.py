import typing

import discord

from vindex.core.i18n import Translator
from vindex.core.utils.formatting import Humanize, inline

if typing.TYPE_CHECKING:
    from prisma.models import Blacklist
    from vindex.core.core_types import Context


_ = Translator("Admin", __file__)


def _base_blacklist_embed(
    blacklist_record: "Blacklist",
    blacklisted_user: discord.User | None,
    blacklist_author: discord.User | None,
) -> discord.Embed:
    embed = discord.Embed(
        title=_("[Blacklist] Entry #{id}").format(id=blacklist_record.id),
        timestamp=blacklist_record.createdAt,
    )

    embed.add_field(
        name=_("Blacklisted ID"),
        value=str(blacklist_record.blacklistedId),
    )
    if blacklisted_user:
        embed.add_field(
            name=_("User information"),
            value=_("Name: {name}\nCreated at: {created_at}\n").format(
                name=blacklisted_user.display_name,
                created_at=Humanize.date(blacklisted_user.created_at),
            ),
        )
        embed.set_thumbnail(url=blacklisted_user.display_avatar.url)
        if blacklisted_user.banner:
            embed.set_image(url=blacklisted_user.banner.url)

    blacklist_delta = discord.utils.utcnow() - blacklist_record.createdAt
    blacklist_update_delta = discord.utils.utcnow() - blacklist_record.updatedAt
    if blacklist_author:
        footer_text = (
            _("Entry by {author} - Update: {update} ago")
            if blacklist_update_delta.total_seconds() > 600
            else _("Entry by {author}")
        )
        embed.set_footer(
            text=footer_text.format(
                author=blacklist_author.name, update=Humanize.timedelta(blacklist_update_delta)
            ),
            icon_url=blacklist_author.display_avatar.url if blacklist_author else None,
        )
    else:
        embed.set_footer(
            text=_("Update: {update} - Created: {create}").format(
                update=Humanize.timedelta(blacklist_update_delta),
                create=Humanize.timedelta(blacklist_delta),
            )
        )

    return embed


async def blacklist_add(ctx: "Context", blacklist_entry: "Blacklist") -> discord.Embed:
    blacklisted_id = int(blacklist_entry.blacklistedId)
    blacklisted_user = await ctx.bot.get_or_fetch_user(blacklisted_id, as_none=True)
    blacklist_author = await ctx.bot.get_or_fetch_user(
        int(blacklist_entry.createdById), as_none=True
    )

    embed = _base_blacklist_embed(blacklist_entry, blacklisted_user, blacklist_author)

    embed.title = _("[Blacklist] Entry #{id} added").format(id=blacklist_entry.id)
    embed.color = discord.Color.dark_red()
    embed.description = _(
        "A new blacklist entry has been added by {author}.\n**Reason**: {reason}"
    ).format(author=inline(str(ctx.author)), reason=blacklist_entry.reason)

    return embed


async def blacklist_remove(
    ctx: "Context", blacklist_entry: "Blacklist", reason: str
) -> discord.Embed:
    blacklisted_id = int(blacklist_entry.blacklistedId)
    blacklisted_user = await ctx.bot.get_or_fetch_user(blacklisted_id, as_none=True)
    blacklist_author = await ctx.bot.get_or_fetch_user(
        int(blacklist_entry.createdById), as_none=True
    )

    embed = _base_blacklist_embed(blacklist_entry, blacklisted_user, blacklist_author)
    embed.title = _("[Blacklist] Entry #{id} removed").format(id=blacklist_entry.id)
    embed.description = _(
        "A blacklist entry has been deleted by {author}.\n**Reason**: {reason}"
    ).format(author=inline(str(ctx.author)), reason=reason)
    embed.color = discord.Color.dark_green()

    embed.add_field(name="Blacklist reason", value=blacklist_entry.reason, inline=False)

    return embed


async def blacklist_check(ctx: "Context", blacklist_entry: "Blacklist") -> discord.Embed:
    blacklisted_id = int(blacklist_entry.blacklistedId)
    blacklisted_user = await ctx.bot.get_or_fetch_user(blacklisted_id, as_none=True)
    blacklist_author = await ctx.bot.get_or_fetch_user(
        int(blacklist_entry.createdById), as_none=True
    )

    embed = _base_blacklist_embed(blacklist_entry, blacklisted_user, blacklist_author)
    embed.color = discord.Color.dark_red()

    if blacklisted_user:
        shared_guilds_str = [
            f"{shared_guild.name} ({shared_guild.id})"
            for shared_guild in blacklisted_user.mutual_guilds
        ]
        embed.add_field(
            name=_("Mutual Guilds"), value=inline("\n".join(shared_guilds_str)), inline=False
        )

    embed.add_field(name=_("Blacklist reason"), value=blacklist_entry.reason, inline=False)

    return embed
