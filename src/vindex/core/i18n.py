import enum
import logging
import pathlib
import typing
from contextvars import ContextVar

import babel.core
import polib
from discord.ext import commands

if typing.TYPE_CHECKING:
    from vindex.core.bot import Vindex
    from vindex.core.core_types import Context, StrPathOrPath


_log = logging.getLogger(__name__)
_current_language = ContextVar("current_language", default="en")


class Languages(enum.Enum):
    """A list of langugages available to the bot."""

    AFRIKAANS = "af"
    CHINESE = "zh"
    DUTCH = "nl"
    ENGLISH = "en"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    JAPANESE = "ja"
    NORWEGIAN = "no"
    POLISH = "pl"
    ROMANIAN = "ro"
    RUSSIAN = "ru"
    SPANISH = "es"

    @classmethod
    async def convert(cls, _: "Context", argument: str):
        """Returns an instance of the Languages class from a string.
        This is meant to be used as a converter for commands.
        """
        try:
            return cls(argument.lower())
        except ValueError as exception:
            raise commands.BadArgument(
                f"The language `{argument}` is not supported."
            ) from exception


def get_babel_current_language() -> babel.core.Locale:
    """Return the current language used by the bot."""
    return babel.core.Locale(_current_language.get())


async def set_language_from_guild(bot: "Vindex", guild_id: int | None = None) -> None:
    """Set the language to use from a guild."""
    language = (
        await bot.services.i18n.get_guild_locale(guild_id) if guild_id else Languages.ENGLISH
    )
    _log.debug("Setting language to %s", language)
    _current_language.set(language.value)


def get_path_to_locales(path: pathlib.Path) -> pathlib.Path:
    """Return the path to the locales folder.

    Parameters
    ----------
    path : pathlib.Path
        The path to the module's directory.

    Returns
    -------
    pathlib.Path
        The path to the locales folder.
    """
    return (path / "locales").resolve()


class Translator:
    """Utility class used to translate strings."""

    module_name: str
    """The name of the module."""

    module_location: pathlib.Path
    """Location of the module's files. Supposedly, ``__file__``."""

    translations: dict[str, dict[str, str]]
    """Dictionnary containing the translations of the module."""

    def __init__(self, module_name: str, file_location: "StrPathOrPath") -> None:
        self.module_name = module_name
        self.module_location = pathlib.Path(file_location).parent.resolve()
        self.translations = {}

        self.load_translations()

    def __call__(self, message: str) -> str:
        # FIXME: Docstrings are not translated!
        try:
            trsnl = self.translations[_current_language.get()][message]
            return trsnl
        except KeyError:
            return message

    def load_translations(self):
        """Load the translations from a module."""
        locales_path = get_path_to_locales(self.module_location)
        if not locales_path.exists():
            _log.warning("No locales folder found for %s", self.module_name)
            return

        for locale_file in locales_path.iterdir():
            if locale_file.suffix != ".po":
                if locale_file.suffix not in (".pot", ".mo"):
                    _log.debug(
                        'Non ".po" file found (%s), ignoring. This should not exist.',
                        str(locale_file),
                    )
                continue

            locale = locale_file.stem
            path = str(locale_file.resolve())
            _log.debug("Loading locale %s from %s", locale, path)
            po_class = polib.pofile(path)

            for entry in po_class:
                if entry.msgstr:
                    _log.log(0, "%s=%s", entry.msgid, entry.msgstr)
                    self.translations.setdefault(locale, {})[entry.msgid] = entry.msgstr
