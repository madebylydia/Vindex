import abc
import typing

if typing.TYPE_CHECKING:
    from vindex.core.bot import Vindex


class Service(typing.Protocol):
    """Base class for all services."""

    bot: "Vindex"
    """The bot instance."""

    @abc.abstractmethod
    async def setup(self) -> None:
        """Setup the service."""
        raise NotImplementedError()
