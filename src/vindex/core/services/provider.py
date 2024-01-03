import typing

from .authorization import AuthorizationService
from .cogs_manager import CogsManager
from .i18n import I18nService

if typing.TYPE_CHECKING:
    from vindex.core.bot import Vindex


class ServiceProvider:
    """The service provider give access to all the services used by the bots.
    Also helps prepare and setup services.
    """

    i18n: I18nService
    """Localization service"""

    authorization: AuthorizationService
    """Authorization service"""

    cogs_manager: CogsManager
    """Cogs manager service"""

    def __init__(self, bot: "Vindex") -> None:
        self.cogs_manager = CogsManager(bot)
        self.authorization = AuthorizationService(bot)
        self.i18n = I18nService(bot)

    async def prepare(self) -> None:
        """Prepare the services.

        This method should probably be ran as a task rather than a coroutine.
        """
        await self.cogs_manager.setup()
        await self.authorization.setup()
        await self.i18n.setup()
