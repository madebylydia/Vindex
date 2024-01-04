import collections.abc
import typing

from vindex.core.services.proto import Service

if typing.TYPE_CHECKING:
    from vindex.core.bot import Vindex


class CompareDict(typing.TypedDict):
    """A typed dict used for the :py:meth:`CogsManager.compare` method."""

    local_not_db: collections.abc.Iterable[str]
    db_not_local: collections.abc.Iterable[str]


class CogsManager(Service):
    """The Cogs manager service will help load and unload cogs from the bot.
    Needed as it interacts with the database too.
    """

    _loaded_cogs: list[str]

    def __init__(self, bot: "Vindex") -> None:
        self.bot = bot
        self._loaded_cogs = []
        super().__init__()

    @property
    def loaded_cogs(self) -> list[str]:
        """Return the loaded cogs list."""
        return self._loaded_cogs

    async def load(self, cog: str):
        """Load a cog using its module name.

        Parameters
        ----------
        cog : str
            The name of the cog to load.

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
        self._loaded_cogs.append(cog)
        await self.bot.database.core.update(where={"id": 1}, data={"cogs": self.loaded_cogs})

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

    async def unload(self, cog: str):
        """Unload a cog using its module name.

        Parameters
        ----------
        cog : str
            The name of the cog to unload.

        Raises
        ------
        ExtensionNotFound
            The name of the extension could not be resolved using the provided package parameter.
        ExtensionNotLoaded
            The extension was not loaded.
        """
        await self.bot.unload_extension(cog)
        self._loaded_cogs.remove(cog)
        await self.bot.database.core.update(where={"id": 1}, data={"cogs": self.loaded_cogs})

    async def compare(self) -> CompareDict:
        """Compare the cogs list inside the database with the loaded cogs."""
        core = await self.bot.database.core.find_unique_or_raise({"id": 1})
        cogs = core.cogs
        return {
            "local_not_db": [cog for cog in self.loaded_cogs if cog not in cogs],
            "db_not_local": [cog for cog in cogs if cog not in self.loaded_cogs],
        }

    # async def update(self) -> None:
    #     """Update the locale cache with the cogs list inside the database."""
    #     core = await self.bot.database.core.find_unique_or_raise({"id": 1})

    async def setup(self) -> None:
        core = await self.bot.database.core.find_unique_or_raise({"id": 1})
        for cog in core.cogs:
            await self.load(cog)
