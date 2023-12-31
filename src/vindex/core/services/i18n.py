import logging
import typing

from vindex.core.services.proto import Service

if typing.TYPE_CHECKING:
    from vindex.core.bot import Vindex


_log = logging.getLogger(__name__)


class I18nService(Service):
    """Utility class used to translate strings."""

    _cache: dict[int, str]

    def __init__(self, bot: "Vindex") -> None:
        self.bot = bot
        self._cache = {}

    async def set_guild_locale(self, guild_id: int, locale: str) -> None:
        """Set the locale for a guild."""
        actual_locale = await self.get_guild_locale(guild_id)
        if actual_locale == locale:
            return
        _log.info("Setting locale for guild %s to %s", guild_id, locale)
        await self.bot.database.guild.upsert(
            where={
                "id": guild_id,
            },
            data={
                "create": {"id": guild_id, "locale": locale},
                "update": {"locale": locale},
            },
        )
        self._cache[guild_id] = locale

    async def get_guild_locale(self, guild_id: int) -> str:
        """Get the locale for a guild."""
        if guild_id in self._cache:
            return self._cache[guild_id]
        guild_data = await self.bot.database.guild.find_unique(
            where={"id": guild_id},
        )
        locale = "en_US" if not guild_data else guild_data.locale
        self._cache[guild_id] = locale
        return locale

    async def setup(self) -> None:
        """Setup the i18n service."""
        guilds = await self.bot.database.guild.find_many()
        for guild in guilds:
            self._cache[guild.id] = guild.locale
        _log.debug("Done caching all guilds locale.")
