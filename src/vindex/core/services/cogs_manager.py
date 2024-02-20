import collections.abc
import keyword
import logging
import pkgutil
import typing

from discord.ext import commands

from prisma.models import LoadedCog
from vindex.core.services.proto import Service

if typing.TYPE_CHECKING:
    from vindex.core.bot import Vindex

_log = logging.getLogger(__name__)


class ReturnLoad(typing.TypedDict):
    """Typed dict for loading cogs."""

    loaded: list[str]
    not_found: list[str]
    already_loaded: list[str]
    failed: list[str]


class ReturnReload(typing.TypedDict):
    """Typed dict for reloading cogs."""

    reloaded: list[str]
    not_found: list[str]
    failed: list[str]


class ReturnUnload(typing.TypedDict):
    """Typed dict for unloading cogs."""

    unloaded: list[str]
    not_found: list[str]
    not_loaded: list[str]


class CogsManager(Service):
    """The Cogs manager service will help load and unload cogs from the bot.
    Needed as it interacts with the database too.
    """

    def __init__(self, bot: "Vindex") -> None:
        self.bot = bot
        super().__init__()

    def available_modules(self) -> list[str]:
        """Return a list of cogs name that can be loaded."""
        modules: list[str] = []

        for _, module_name, _ in pkgutil.iter_modules(
            [pkgutil.resolve_name("vindex.cogs").__path__[0]]
        ):
            if module_name.isidentifier() and not keyword.iskeyword(module_name):
                modules.append(module_name)
        return modules

    async def load(
        self, cogs: collections.abc.Iterable[str], /, *, append_db: bool = True
    ) -> ReturnLoad:
        """Load a cog using its module name.

        Parameters
        ----------
        cogs : str
            The name of the cogs to load.
        append_db : bool
            Whether to append the cog to the database or not once loaded.

        Returns
        -------
        dict
            A dictionary containing the loaded cogs, the cogs that were not found, the cogs that
            were already loaded and the cogs that failed to load. Typed.
        """
        loaded: list[str] = []
        not_found: list[str] = []
        already_loaded: list[str] = []
        failed: list[str] = []

        for cog in cogs:
            try:
                await self.bot.load_extension(cog)
                loaded.append(cog)
                if append_db:
                    await LoadedCog.prisma().create(data={"name": cog})
            except (commands.errors.ExtensionNotFound, ModuleNotFoundError):
                not_found.append(cog)
            except commands.errors.ExtensionAlreadyLoaded:
                already_loaded.append(cog)
            except commands.errors.ExtensionError:
                _log.error("An error occured while loading %s", cog, exc_info=True)
                failed.append(cog)
        return ReturnLoad(
            loaded=loaded, not_found=not_found, already_loaded=already_loaded, failed=failed
        )

    async def reload(self, cogs: collections.abc.Iterable[str]):
        """Reload a cog using its module name.

        Parameters
        ----------
        cogs : str
            The name of the cogs to reload.

        Returns
        -------
        dict
            A dictionary containing the reloaded cogs, the cogs that were not found and the cogs
            that failed to reload. Typed.
        """
        # TODO: Remove cog if reload fails
        reloaded: list[str] = []
        not_found: list[str] = []
        failed: list[str] = []

        for cog in cogs:
            try:
                await self.bot.reload_extension(cog)
                reloaded.append(cog)
            except (commands.errors.ExtensionNotFound, ModuleNotFoundError):
                not_found.append(cog)
            except commands.errors.ExtensionNotLoaded:
                result = await self.load(cog)
                if result["not_found"]:
                    not_found.append(cog)
                if result["failed"]:
                    failed.append(cog)
                if result["loaded"]:
                    reloaded.append(cog)
            except commands.errors.ExtensionError:
                _log.error("An error occured while reloading %s", cog, exc_info=True)
                failed.append(cog)
        return ReturnReload(reloaded=reloaded, not_found=not_found, failed=failed)

    async def unload(
        self, cogs: collections.abc.Iterable[str], /, *, append_db: bool = True
    ) -> ReturnUnload:
        """Unload a cog using its module name.

        Parameters
        ----------
        cogs : Iterable of str
            The name of the cogs to unload.
        append_db : bool
            Whether to append the cog to the database or not once unloaded.

        Returns
        -------
        dict
            A dictionary containing the unloaded cogs, the cogs that were not found and the cogs
            that were not loaded. Typed.
        """
        unloaded: list[str] = []
        not_found: list[str] = []
        not_loaded: list[str] = []

        for cog in cogs:
            try:
                await self.bot.unload_extension(cog)
                unloaded.append(cog)
                if append_db:
                    await LoadedCog.prisma().delete(where={"name": cog})
            except (commands.errors.ExtensionNotFound, ModuleNotFoundError):
                not_found.append(cog)
            except commands.errors.ExtensionNotLoaded:
                not_loaded.append(cog)

        return ReturnUnload(unloaded=unloaded, not_found=not_found, not_loaded=not_loaded)

    # async def compare(self) -> CompareDict:
    #     """Compare the cogs list inside the database with the loaded cogs."""
    #     cogs = await ExternalCog.prisma().find_many()
    #     if not cogs:
    #         cogs = []
    #     else:
    #         cogs = [cog.path for cog in cogs]
    #     return {
    #         "local_not_db": [cog for cog in self.bot.extensions if cog not in cogs],
    #         "db_not_local": [cog for cog in cogs if cog not in self.bot.extensions],
    #     }

    async def setup(self) -> None:
        """Setup the cogs manager service."""
        cogs = await LoadedCog.prisma().find_many()
        await self.load([cog.name for cog in cogs], append_db=False)
