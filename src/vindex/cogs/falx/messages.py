import typing

import discord

from vindex.core.i18n import Translator
from vindex.core.utils.formatting import Humanize, inline, reduce_to

if typing.TYPE_CHECKING:
    from prisma.models import GuildAllowance
    from vindex.core.bot import Vindex


_ = Translator("Falx", __file__)


def _base_falx_embed(guild: discord.Guild) -> discord.Embed:
    embed = discord.Embed(title="[Falx] Report (Base)")

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    if guild.splash:
        embed.set_image(url=guild.splash.url)

    embed.add_field(
        name=_("Guild information"),
        value=_(
            "**Name**: {name}\n**ID**: {id}\n**Created at**: {created_at}\n"
            "**Preferred locale**: {preferred_locale}\n**Vanity URL**: {vanity_url}\n"
            "**Chunked**: {chunked}"
        ).format(
            name=guild.name,
            id=guild.id,
            created_at=Humanize.date(guild.created_at),
            preferred_locale=guild.preferred_locale,
            vanity_url=str(guild.vanity_url_code),
            chunked=guild.chunked,
        ),
    )
    if guild.owner:
        shared_guilds = [
            f"{shared_guild.name} ({shared_guild.id})"
            for shared_guild in guild.owner.mutual_guilds
        ]

        embed.add_field(
            name=_("Owner information"),
            value=_(
                "**Name**: {name}\n**ID**: {id}\n**Created at**: {created_at}\n"
                "**Known in**:\n{known_in}\n"
            ).format(
                name=guild.owner.name,
                id=guild.owner.id,
                created_at=Humanize.date(guild.owner.created_at),
                known_in="\n".join(shared_guilds),
            ),
        )

    humans = len([human for human in guild.members if not human.bot])
    bots = len([human for human in guild.members if human.bot])
    percentage = bots / guild.member_count * 100 if guild.member_count else None
    embed.add_field(
        name=_("Members insights"),
        value=_(
            "{member_count} members.\n{humans} humans.\n{bots} bots.\nRatio: {ratio}% bots."
        ).format(
            member_count=inline(Humanize.number(len(guild.members))),
            humans=inline(Humanize.number(humans)),
            bots=inline(Humanize.number(bots)),
            ratio=Humanize.number(percentage) if percentage else "N/A",
        ),
        inline=False,
    )

    return embed


def falx_join(guild: discord.Guild, is_allowed: bool) -> discord.Embed:
    embed = _base_falx_embed(guild)

    embed.title = f"[Falx] New guild: {guild.name}"

    if is_allowed:
        embed.description = _("This guild has been allowed.")
        embed.color = discord.Color.green()
    else:
        embed.description = _("This guild has not been allowed. It'll now leave.")
        embed.color = discord.Color.red()

    return embed


def falx_leave(guild: discord.Guild) -> discord.Embed:
    embed = _base_falx_embed(guild)

    embed.title = f"[Falx] Left guild: {guild.name}"
    embed.color = discord.Color.dark_orange()

    return embed


def falx_startup(
    disallowed_guilds: list[discord.Guild],
    unknown_guilds: list[discord.Guild],
) -> discord.Embed:
    total_acted_guilds = len(disallowed_guilds) + len(unknown_guilds)

    if disallowed_guilds:
        color = discord.Color.red()
    else:
        color = discord.Color.orange()

    embed = discord.Embed(title=_("[Falx] Cog Startup report"), color=color)
    embed.description = _(
        "During Falx startup, {total_acted_guilds} guilds were found as orphans."
    ).format(total_acted_guilds=inline(str(total_acted_guilds)))

    if disallowed_guilds:
        embed.add_field(
            name=_("Left guilds"),
            value=reduce_to(Humanize.list([guild.name for guild in disallowed_guilds]), 1024),
        )
    if unknown_guilds:
        embed.add_field(
            name=_("Unknown guilds"),
            value=reduce_to(Humanize.list([guild.name for guild in unknown_guilds]), 1024),
        )

    return embed


def falx_check(bot: "Vindex", allowance_record: "GuildAllowance") -> discord.Embed:
    embed = discord.Embed(
        title=f"[Falx] Allowance for ID {allowance_record.id}",
        color=discord.Color.green() if allowance_record.allowed else discord.Color.red(),
        description=_(
            "This guild has been allowed since {days}."
            if allowance_record.allowed
            else "This guild has been denied since {days}."
        ).format(days=Humanize.timedelta(allowance_record.createdAt)),
    )

    is_bot_mod = bot.is_bot_mod_id(int(allowance_record.createdById))
    embed.add_field(
        name=_("Allowed by"),
        value=_("**ID**: {id}\n**Bot mod**: {is_bot_mod}").format(
            id=allowance_record.createdById, is_bot_mod=is_bot_mod
        ),
    )

    embed.add_field(name=_("Allowed at"), value=Humanize.date(allowance_record.createdAt))
    embed.add_field(name=_("Allowance reason"), value=allowance_record.allowanceReason)

    embed.set_footer(
        text=_("Last updated at {last_updated}").format(
            last_updated=Humanize.timedelta(allowance_record.updatedAt)
        )
    )

    return embed
