import abc
import typing

from discord.ext import commands

from vindex.core.services.provider import ServiceProvider

if typing.TYPE_CHECKING:
    from prisma import Prisma
    from vindex.core.creator.model import Creator


class ABCVindex(commands.AutoShardedBot, abc.ABC):
    """ABC class for the Vindex class.
    Permits the usage of type-hinting for any classes that requires the Vindex's class attributes.
    """

    creator: "Creator"
    """The Creator used to create the bot instance."""

    database: "Prisma"
    """The database linked to the bot instance.
    Connected once the bot is ready. (During ``setup_hook``)
    """

    services: ServiceProvider
    """A list of services available to the bot.
    Contain services like i18n, blacklist management, authorization, etc.
    """
