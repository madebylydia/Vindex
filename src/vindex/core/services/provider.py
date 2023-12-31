import typing

from .authorization import AuthorizationService
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

    def __init__(self, bot: "Vindex") -> None:
        self.i18n = I18nService(bot)
        self.authorization = AuthorizationService(bot)

    async def prepare(self) -> None:
        """Prepare the services.

        This method should probably be ran as a task rather than a coroutine.
        """
        await self.i18n.setup()
        await self.authorization.setup()
