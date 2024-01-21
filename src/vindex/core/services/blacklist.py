import typing

import discord
from prisma.models import Blacklist

from vindex.core.services.proto import Service

if typing.TYPE_CHECKING:
    from vindex.core.bot import Vindex


class BlacklistService(Service):
    """Services used to manage blacklisted users."""

    blacklisted_ids: list[int]

    def __init__(self, bot: "Vindex") -> None:
        self.bot = bot
        super().__init__()

    async def add_to_blacklist(
        self, author: discord.abc.User, user_id: int, reason: str
    ) -> Blacklist | None:
        """Add an user to the blacklist.

        Parameters
        ----------
        author : discord.abc.User
            The user who is adding the user to the blacklist.
        user_id : int
            The id of the user to add to the blacklist.
        reason : str
            The reason for adding the user to the blacklist.

        Returns
        -------
        bool
            Whether the user was added to the blacklist or not.
        """
        if self.is_blacklisted(user_id):
            return None

        case = await Blacklist.prisma().create(
            data={
                "id": user_id,
                "reason": reason,
                "blacklistedById": author.id,
            }
        )
        self.blacklisted_ids.append(user_id)

        return case

    async def remove_from_blacklist(self, user_id: int) -> Blacklist | None:
        """Remove an user from the blacklist.

        Parameters
        ----------
        user_id : int
            The id of the user to remove from the blacklist.

        Returns
        -------
        Blacklist or None
            Whether the user was removed from the blacklist or not.
        """
        if not self.is_blacklisted(user_id):
            return None

        case = await Blacklist.prisma().delete(where={"id": user_id})
        self.blacklisted_ids.remove(user_id)

        return case

    async def get_blacklist(self, user_id: int) -> Blacklist | None:
        """Get the blacklist entry for an user.

        Parameters
        ----------
        user_id : int
            The id of the user to get the blacklist entry for.

        Returns
        -------
        prisma.models.Blacklist
            The blacklist entry for the user.
        """
        return await Blacklist.prisma().find_unique(
            where={"id": user_id}, include={"blacklistedBy": True}
        )

    def is_blacklisted(self, user_id: int, /) -> bool:
        """Check if an user is blacklisted.

        Parameters
        ----------
        user_id : int
            The id of the user to check.

        Returns
        -------
        bool
            Whether the user is blacklisted or not.
        """
        return user_id in self.blacklisted_ids

    async def setup(self) -> None:
        """Prepare the service."""
        self.blacklisted_ids = [case.id for case in await Blacklist.prisma().find_many()]
