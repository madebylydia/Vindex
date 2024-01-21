import logging
import typing

from prisma.models import Guild

from vindex.core.i18n import Languages
from vindex.core.services.proto import Service

if typing.TYPE_CHECKING:
    from vindex.core.bot import Vindex


_log = logging.getLogger(__name__)


class I18nService(Service):
    """Utility class used to translate strings."""

    _cache: dict[int, "Languages"]

    def __init__(self, bot: "Vindex") -> None:
        self.bot = bot
        self._cache = {}

    async def set_guild_locale(self, guild_id: int, locale: "Languages") -> None:
        """Set the locale for a guild."""
        actual_locale = await self.get_guild_locale(guild_id)
        if actual_locale == locale:
            return
        _log.info("Setting locale for guild %s to %s", guild_id, locale)
        await Guild.prisma().upsert(
            where={
                "id": guild_id,
            },
            data={
                "create": {"id": guild_id, "locale": locale.value},
                "update": {"locale": locale.value},
            },
        )
        self._cache[guild_id] = locale

    async def get_guild_locale(self, guild_id: int) -> "Languages":
        """Get the locale for a guild."""
        if guild_id in self._cache:
            _log.debug("Using cached locale for guild %s", guild_id)
            return self._cache[guild_id]
        guild_data = await Guild.prisma().find_unique(
            where={"id": guild_id},
        )
        locale = Languages.ENGLISH if not guild_data else Languages(guild_data.locale)
        _log.debug("Cached locale for guild %s: %s", guild_id, locale)
        self._cache[guild_id] = locale
        return locale

    async def setup(self) -> None:
        """Setup the i18n service."""
        guilds = await Guild.prisma().find_many()
        for guild in guilds:
            self._cache[guild.id] = Languages(guild.locale)
        _log.debug("Done caching all guilds locale.")
