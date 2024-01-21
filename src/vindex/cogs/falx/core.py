import typing

import discord
from discord.ext import commands
from discord.utils import utcnow
from prisma.models import Guild

from vindex.core.checks import is_bot_mod
from vindex.core.i18n import Translator
from vindex.core.ui.formatting import Humanize, inline
from vindex.core.ui.prompt import ConfirmView

if typing.TYPE_CHECKING:
    from prisma import Client
    from vindex.core.bot import Vindex
    from vindex.core.core_types import Context


_ = Translator("Falx", __file__)


class Falx(commands.Cog):
    """The guild authorization layer of Vindex."""

    bot: "Vindex"
    db: "Client"

    def __init__(self, bot: "Vindex") -> None:
        self.bot = bot
        self.db = bot.database
        super().__init__()

    async def is_guild_allowed(self, guild_id: int):
        guild_data = await Guild.prisma().find_unique(where={"id": guild_id})
        if not guild_data:
            return False
        return guild_data.allowed

    def build_join_embed(self, guild: discord.Guild, is_allowed: bool | None) -> discord.Embed:
        embed = discord.Embed()

        embed.title = f"[Falx] I've joined {guild.name}"

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        if guild.splash:
            embed.set_image(url=guild.splash.url)

        if is_allowed:
            embed.description = _("This guild is allowed to use the bot. It'll now stay.")
            embed.color = discord.Color.green()
        else:
            embed.description = _("This guild is not allowed to use the bot. It'll now leave.")
            embed.color = discord.Color.red()

        if guild.owner:
            shared_guilds_str = [
                f"- {shared_guild.name} ({shared_guild.id})"
                for shared_guild in guild.owner.mutual_guilds
            ]
            embed.add_field(
                name=_("Owner information"),
                value=_(
                    "**Name:** {name}\n**ID:** {id}\n**Created at:** {created_at}\n"
                    "**Known in:**\n{known_in}\n"
                ).format(
                    name=inline(guild.owner.name),
                    id=guild.owner.id,
                    created_at=guild.owner.created_at,
                    known_in="\n".join(shared_guilds_str),
                ),
            )

        embed.add_field(
            name=_("Guild information"),
            value=_(
                "**Name:** {name}\n**ID:** {id}\n**Created at:** {created_at}\n"
                "**Preferred locale:** {preferred_locale}\n**Vanity URL:** {vanity_url}\n"
            ).format(
                name=guild.name,
                id=inline(str(guild.id)),
                created_at=guild.created_at,
                preferred_locale=guild.preferred_locale,
                vanity_url=str(guild.vanity_url_code),
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

        embed.set_footer(
            text=_("Operating with a role: {possible_role}").format(
                possible_role=bool(guild.self_role)
            )
        )

        return embed

    def build_leave_embed(self, guild: discord.Guild) -> discord.Embed:
        embed = discord.Embed()

        embed.title = f"[Falx] I've left {guild.name}"
        embed.color = discord.Color.gold()

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        if guild.splash:
            embed.set_image(url=guild.splash.url)

        owned_embed = None
        if guild.owner:
            shared_guilds_str = [
                f"{shared_guild.name} ({shared_guild.id})"
                for shared_guild in guild.owner.mutual_guilds
            ]
            owned_embed = embed.add_field(
                name=_("Owner information"),
                value=_(
                    "**Name:** {name}\n**ID:** {id}\n**Created at:** {created_at}\n"
                    "**Known in:**\n{known_in}\n"
                ).format(
                    name=inline(guild.owner.name),
                    id=inline(str(guild.owner.id)),
                    created_at=guild.owner.created_at,
                    known_in="\n".join(shared_guilds_str),
                ),
            )
        if owned_embed is None and guild.owner_id:
            embed.add_field(
                name=_("Owner ID"),
                value=inline(str(guild.owner_id)),
            )

        embed.add_field(
            name=_("Guild information"),
            value=_(
                "**Name:** {name}\n**ID:** {id}\n**Created at:** {created_at}\n"
                "**Preferred locale:** {preferred_locale}\n**Vanity URL:** {vanity_url}\n"
            ).format(
                name=inline(str(guild.name)),
                id=inline(str(guild.id)),
                created_at=guild.created_at,
                preferred_locale=guild.preferred_locale,
                vanity_url=str(guild.vanity_url_code),
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
                ratio=Humanize.number(round(percentage, 1)) if percentage else "N/A",
            ),
            inline=False,
        )

        if guild.me and guild.me.joined_at:
            embed.set_footer(
                text=(
                    "This guild was joined "
                    f"{Humanize.number((utcnow() - guild.me.joined_at).days)} days ago."
                ),
                icon_url=guild.me.display_avatar.url,
            )
        else:
            assert self.bot.user
            embed.set_footer(
                text=(
                    "Unable to determine when the guild was joined. (Missing "
                    "information about the bot in the guild)"
                ),
                icon_url=self.bot.user.display_avatar.url,
            )

        return embed

    @commands.group(name="falx")
    @is_bot_mod()
    async def cmd_falx(self, ctx: "Context"):
        """Guild authorization layer of Vindex."""

    @cmd_falx.command(name="seed")
    async def cmd_falx_seed(self, ctx: "Context"):
        """Seed existing guilds. This will allow all guilds the bot has already joined."""
        async with (ConfirmView(ctx, content=_("Are you sure you want to seed all guilds?"))) as (
            confirmed,
            __,
        ):
            if not confirmed:
                return

        count = 0
        for guild in self.bot.guilds:
            await Guild.prisma().upsert(
                where={"id": guild.id},
                data={
                    "create": {
                        "id": guild.id,
                        "allowed": True,
                        "allowanceBy": {"connect": {"id": ctx.author.id}},
                        "allowanceAt": utcnow(),
                        "allowanceReason": f"Automatic seeding of {guild.name} by {ctx.author.id}",
                    },
                    "update": {
                        "allowed": True,
                        "allowanceBy": {"connect": {"id": ctx.author.id}},
                        "allowanceAt": utcnow(),
                        "allowanceReason": f"Automatic seeding of {guild.name} by {ctx.author.id}",
                    },
                },
            )
            count += 1

        await ctx.send(_("Done. {count} guilds were succesfully seeded.").format(count=count))

    @cmd_falx.command(name="add")
    async def cmd_falx_add(self, ctx: "Context", guild_or_id: discord.Guild | int, *, reason: str):
        """Allow a guild to use Vindex."""
        guild_id = guild_or_id if isinstance(guild_or_id, int) else guild_or_id.id

        guild_data = await Guild.prisma().find_first(where={"id": guild_id})
        if guild_data and guild_data.allowed:
            await ctx.send(_("This guild is already allowed."))
            return

        await Guild.prisma().upsert(
            where={"id": guild_id},
            data={
                "create": {
                    "id": guild_id,
                    "allowed": True,
                    "allowanceBy": {"connect": {"id": ctx.author.id}},
                    "allowanceAt": utcnow(),
                    "allowanceReason": reason,
                },
                "update": {
                    "allowed": True,
                    "allowanceBy": {"connect": {"id": ctx.author.id}},
                    "allowanceAt": utcnow(),
                    "allowanceReason": reason,
                },
            },
        )
        await ctx.send(_("This guild has now been allowed."))

    @cmd_falx.command(name="remove")
    async def cmd_falx_remove(
        self,
        ctx: "Context",
        guild_or_id: discord.Guild | int,
        *,
        reason: str,
    ):
        """Disallow a guild to use Vindex."""
        guild_id = guild_or_id if isinstance(guild_or_id, int) else guild_or_id.id

        guild_data = await Guild.prisma().find_first(where={"id": guild_id})
        if not guild_data or not guild_data.allowed:
            await ctx.send(_("This guild is already disallowed."))
            return

        await Guild.prisma().upsert(
            where={"id": guild_id},
            data={
                "create": {
                    "id": guild_id,
                    "allowed": False,
                    "allowanceAt": utcnow(),
                    "allowanceBy": {"connect": {"id": ctx.author.id}},
                    "allowanceReason": reason,
                },
                "update": {
                    "allowed": False,
                    "allowanceAt": utcnow(),
                    "allowanceBy": {"connect": {"id": ctx.author.id}},
                    "allowanceReason": reason,
                },
            },
        )

        fetched_guild = self.bot.get_guild(guild_id)
        if fetched_guild:
            async with ConfirmView(
                ctx, content=_("Disallowed. I am still in this guild. Do you wish me to leave it?")
            ) as (confirmed, __):
                if confirmed:
                    await fetched_guild.leave()
        else:
            await ctx.send(_("This guild is now disallowed."))

    @cmd_falx.command(name="check")
    async def cmd_falx_check(self, ctx: "Context", guild_or_id: discord.Guild | int):
        """Check if a guild is allowed to use Vindex."""
        guild_id = guild_or_id if isinstance(guild_or_id, int) else guild_or_id.id

        guild_data = await Guild.prisma().find_unique(
            where={"id": guild_id}, include={"allowanceBy": True}
        )
        if not guild_data:
            await ctx.send(_("No, this guild is not allowed and I've found no record."))
            return

        embed = discord.Embed(
            title=f"Falx report for {guild_data.id}",
        )
        match guild_data.allowed:
            case True:
                assert guild_data.allowanceAt
                allowed_since = utcnow() - guild_data.allowanceAt
                embed.color = discord.Color.green()
                embed.description = _("This guild has been allowed since {days} days.").format(
                    days=allowed_since.days
                )
            case False:
                assert guild_data.allowanceAt
                allowed_since = utcnow() - guild_data.allowanceAt
                embed.color = discord.Color.red()
                embed.description = _("This guild has been disallowed since {days} days.").format(
                    days=allowed_since.days
                )
            case None:
                embed.color = discord.Color.dark_gray()
                embed.description = _("This guild has never been allowed nor disallowed.")
                await ctx.send(embed=embed)
                return

        assert guild_data.allowanceAt
        assert guild_data.allowanceById
        assert guild_data.allowanceReason

        allowance_user = await self.bot.get_or_fetch_user(guild_data.allowanceById, as_none=True)

        embed.add_field(
            name=_("Allowed by"),
            value=_("{user_id} - Is bot moderator: {is_bot_moderator}").format(
                user_id=inline(str(guild_data.allowanceById)),
                is_bot_moderator=guild_data.allowanceBy.isBotMod
                if guild_data.allowanceBy
                else _("Unknown"),
            ),
        )
        embed.add_field(
            name=_("Allowed at"),
            value=str(guild_data.allowanceAt),
        )
        embed.add_field(
            name=_("Allowed reason"),
            value=guild_data.allowanceReason,
        )
        embed.add_field(
            name=_("Currently in guild"),
            value=str(bool(self.bot.get_guild(guild_data.id))),
        )

        if allowance_user:
            embed.set_footer(
                text=_("Allowance by {user}").format(user=allowance_user.display_name),
                icon_url=allowance_user.display_avatar.url,
            )

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """Handle guild join events."""
        allowed = await self.is_guild_allowed(guild.id)
        await self.bot.core_notify(embeds=[self.build_join_embed(guild, allowed)])
        if not allowed:
            await guild.leave()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        """Handle guild leave events."""
        allowed = await self.is_guild_allowed(guild.id)

        if not allowed:
            # We already sent the on_guild_join embed that is above. No need for the leave embed.
            return

        await Guild.prisma().update(
            where={"id": guild.id},
            data={
                "allowed": False,
                "allowanceAt": utcnow(),
                "allowanceReason": "Guild was left, allowance removed by bot.",
            },
        )
        await self.bot.core_notify(embeds=[self.build_leave_embed(guild)])
