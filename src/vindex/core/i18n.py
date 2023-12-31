import enum
import gettext
import logging
import pathlib
import typing
from contextvars import ContextVar

if typing.TYPE_CHECKING:
    from vindex.core.bot import Vindex
    from vindex.core.core_types import StrPathOrPath


_log = logging.getLogger(__name__)
_corrent_language = ContextVar("current_language", default="en_US")


class Languages(enum.Enum):
    """A list of langugages available to the bot."""

    ENGLISH = "en_US"
    FRENCH = "fr_FR"
    GERMAN = "de_DE"
    RUSSIAN = "ru_RU"
    SPANISH = "es_ES"
    ITALIAN = "it_IT"


async def set_language_from_guild(bot: "Vindex", guild_id: int | None = None) -> None:
    """Set the language to use from a guild."""
    if guild_id:
        language = await bot.services.i18n.get_guild_locale(guild_id)
    else:
        language = "en_US"
    _log.debug("Setting language to %s", language)
    _corrent_language.set(language)


class Translator:
    """Utility class used to translate strings."""

    cog_name: str
    """The name of the cog."""

    cog_location: pathlib.Path
    """Location of the cog's files."""

    def __init__(self, cog_name: str, file_location: "StrPathOrPath") -> None:
        self.cog_name = cog_name

        self.cog_location = pathlib.Path(file_location).parent

    def __call__(self, message: str) -> str:
        return gettext.gettext(message)
