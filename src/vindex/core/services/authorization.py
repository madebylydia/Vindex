import enum
import logging
import typing

import discord

from vindex.core.i18n import Translator
from vindex.core.services.proto import Service
from vindex.core.ui.formatting import inline

if typing.TYPE_CHECKING:
    from vindex.core.bot import Vindex


_log = logging.getLogger(__name__)


class AuthorizationColor(enum.Enum):
    """The colors used for the embeds."""

    ALLOWED = discord.Color.brand_green()
    DISALLOWED = discord.Color.brand_red()


_ = Translator("AuthorizationService", __file__)


class AuthorizationService(Service):
    """The Autorization service is used to allow certains guilds to use the bot."""

    _cache: dict[int, bool] = {}

    def __init__(self, bot: "Vindex") -> None:
        self.bot = bot
        super().__init__()

    def build_embed(self, guild: discord.Guild, is_allowed: bool) -> discord.Embed:
        embed = discord.Embed()
        embed.title = f"{guild.name} ({guild.id})"
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        if guild.splash:
            embed.set_image(url=guild.splash.url)

        if is_allowed:
            embed.description = _("This guild is allowed to use the bot. It'll now stay.")
            embed.color = AuthorizationColor.ALLOWED.value
        else:
            embed.description = _("This guild is not allowed to use the bot. It'll now leave.")
            embed.color = AuthorizationColor.DISALLOWED.value

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

        humans = len([human for human in guild.members if not human.bot])
        bots = len([human for human in guild.members if human.bot])
        percentage = bots / guild.member_count * 100 if guild.member_count else None
        embed.add_field(
            name=_("Members count"),
            value=_(
                "{member_count} members.\n{humans} humans.\n{bots} bots.\nRatio: "
                "{percentage}% bots."
            ).format(
                member_count=inline(str(guild.member_count)),
                humans=inline(str(humans)),
                bots=inline(str(bots)),
                percentage=round(percentage) if percentage else "N/A",
            ),
        )

        assert self.bot.user is not None
        embed.set_footer(
            text="This guild was approved."
            if is_allowed
            else "This guild was left automatically as it hasn't been approved.",
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None,
        )

        return embed

    async def allow(self, guild_id: int):
        """Allow a guild to use the bot."""
        if guild_id in self._cache:
            if self._cache[guild_id]:
                return
        await self.bot.database.guild.upsert(
            where={"id": guild_id},
            data={
                "create": {
                    "id": guild_id,
                    "locale": "en",
                    "allowed": True,
                },
                "update": {"allowed": True},
            },
        )
        self._cache[guild_id] = True

    async def disallow(self, guild_id: int):
        """Unallow a guild to use the bot."""
        if guild_id in self._cache:
            if not self._cache[guild_id]:
                return
        await self.bot.database.guild.upsert(
            where={"id": guild_id},
            data={
                "create": {
                    "id": guild_id,
                    "locale": "en",
                    "allowed": False,
                },
                "update": {"allowed": False},
            },
        )
        self._cache[guild_id] = False

    async def is_allowed(self, guild_id: int) -> bool:
        """Check if a guild is allowed to use the bot."""
        guild_data = await self.bot.database.guild.find_unique(where={"id": guild_id})
        if not guild_data:
            return False
        if guild_id not in self._cache:
            self._cache[guild_id] = guild_data.allowed
        return self._cache[guild_id]

    async def handle_new_guild(self, guild: discord.Guild) -> None:
        """Handles the join of a new guild.

        Parameters
        ----------
        guild : discord.Guild
            The guild that joined.
        """
        assert self.bot.user is not None
        is_allowed = await self.is_allowed(guild.id)

        await self.bot.core_notify(
            content=f"{self.bot.user.name} has joined a new guild: {guild.name} ({guild.id})",
            embeds=[self.build_embed(guild, is_allowed)],
        )

        if is_allowed:
            _log.debug(_("Guild %s (%s) is allowed to use the bot."), guild.name, guild.id)
            return

        _log.debug(_("Guild %s (%s) is unallowed to use the bot, leaving"), guild.name, guild.id)
        await guild.leave()

    async def setup(self) -> None:
        """Setup the autorization service."""
        guilds = await self.bot.database.guild.find_many()
        for guild in guilds:
            self._cache[guild.id] = guild.allowed
        _log.debug("Done caching all guilds autorization.")
