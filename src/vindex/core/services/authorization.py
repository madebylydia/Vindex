import logging
import typing

from vindex.core.services.proto import Service

if typing.TYPE_CHECKING:
    import discord

    from vindex.core.bot import Vindex


_log = logging.getLogger(__name__)


class AuthorizationService(Service):
    """The Autorization service is used to allow certains guilds to use the bot."""

    _cache: dict[int, bool] = {}

    def __init__(self, bot: "Vindex") -> None:
        self.bot = bot
        super().__init__()

    async def allow(self, guild: "discord.Guild"):
        """Allow a guild to use the bot."""
        if guild.id in self._cache:
            if self._cache[guild.id]:
                return
        await self.bot.database.guild.upsert(
            where={"id": guild.id},
            data={
                "create": {
                    "id": guild.id,
                    "locale": guild.preferred_locale.value,
                    "allowed": True,
                },
                "update": {"allowed": True},
            },
        )
        self._cache[guild.id] = True

    async def disallow(self, guild: "discord.Guild"):
        """Unallow a guild to use the bot."""
        if guild.id in self._cache:
            if not self._cache[guild.id]:
                return
        await self.bot.database.guild.upsert(
            where={"id": guild.id},
            data={
                "create": {
                    "id": guild.id,
                    "locale": guild.preferred_locale.value,
                    "allowed": False,
                },
                "update": {"allowed": False},
            },
        )
        self._cache[guild.id] = False

    async def is_allowed(self, guild: "discord.Guild") -> bool:
        """Check if a guild is allowed to use the bot."""
        guild_data = await self.bot.database.guild.find_unique(where={"id": guild.id})
        if not guild_data:
            return False
        if guild.id not in self._cache:
            self._cache[guild.id] = guild_data.allowed
        return self._cache[guild.id]

    async def setup(self) -> None:
        """Setup the autorization service."""
        guilds = await self.bot.database.guild.find_many()
        for guild in guilds:
            self._cache[guild.id] = guild.allowed
        _log.debug("Done caching all guilds autorization.")
