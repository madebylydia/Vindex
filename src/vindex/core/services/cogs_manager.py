import collections.abc
import logging
import typing

from prisma.models import ExternalCog

from vindex.core.services.proto import Service

if typing.TYPE_CHECKING:
    from vindex.core.bot import Vindex

_log = logging.getLogger(__name__)


class CompareDict(typing.TypedDict):
    """A typed dict used for the :py:meth:`CogsManager.compare` method."""

    local_not_db: collections.abc.Iterable[str]
    db_not_local: collections.abc.Iterable[str]


class CogsManager(Service):
    """The Cogs manager service will help load and unload cogs from the bot.
    Needed as it interacts with the database too.
    """

    def __init__(self, bot: "Vindex") -> None:
        self.bot = bot
        super().__init__()

    async def load(self, cog: str, /, *, append_db: bool = True):
        """Load a cog using its module name.

        Parameters
        ----------
        cog : str
            The name of the cog to load.
        append_db : bool
            Whether to append the cog to the database or not once loaded.

        Raises
        ------
        ExtensionNotFound
            The extension could not be imported. This is also raised if the name of the extension
            could not be resolved using the provided package parameter.
        ExtensionAlreadyLoaded
            The extension is already loaded.
        NoEntryPointError
            The extension does not have a setup function.
        ExtensionFailed
            The extension or its setup function had an execution error.
        """
        await self.bot.load_extension(cog)
        if append_db:
            _log.debug("Appending/Loading %s to the database", cog)
            await ExternalCog.prisma().upsert(
                where={
                    "path": cog,
                },
                data={
                    "create": {
                        "path": cog,
                        "loaded": True,
                    },
                    "update": {
                        "loaded": True,
                    },
                },
            )

    async def reload(self, cog: str):
        """Reload a cog using its module name.

        Parameters
        ----------
        cog : str
            The name of the cog to reload.

        Raises
        ------
        ExtensionNotLoaded
            The extension was not loaded.
        ExtensionNotFound
            The extension could not be imported. This is also raised if the name of the extension
            could not be resolved using the provided package parameter.
        NoEntryPointError
            The extension does not have a setup function.
        ExtensionFailed
            The extension setup function had an execution error.
        """
        # TODO: Remove cog if reload fails
        await self.bot.reload_extension(cog)

    async def unload(self, cog: str, /, *, append_db: bool = True):
        """Unload a cog using its module name.

        Parameters
        ----------
        cog : str
            The name of the cog to unload.
        append_db : bool
            Whether to append the cog to the database or not once unloaded.

        Raises
        ------
        ExtensionNotFound
            The name of the extension could not be resolved using the provided package parameter.
        ExtensionNotLoaded
            The extension was not loaded.
        """
        await self.bot.unload_extension(cog)
        if append_db:
            _log.debug("Appending/Unloading %s to the database", cog)
            await ExternalCog.prisma().upsert(
                where={
                    "path": cog,
                },
                data={
                    "create": {
                        "path": cog,
                        "loaded": False,
                    },
                    "update": {
                        "loaded": False,
                    },
                },
            )

    async def compare(self) -> CompareDict:
        """Compare the cogs list inside the database with the loaded cogs."""
        cogs = await ExternalCog.prisma().find_many()
        if not cogs:
            cogs = []
        else:
            cogs = [cog.path for cog in cogs]
        return {
            "local_not_db": [cog for cog in self.bot.extensions if cog not in cogs],
            "db_not_local": [cog for cog in cogs if cog not in self.bot.extensions],
        }

    async def setup(self) -> None:
        cogs = await ExternalCog.prisma().find_many(where={"loaded": True})
        for cog in cogs:
            await self.load(cog.path, append_db=False)
