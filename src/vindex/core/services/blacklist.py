import typing

import discord

import prisma
from vindex.core.services.proto import Service

if typing.TYPE_CHECKING:
    from vindex.core.bot import Vindex


class BlacklistService(Service):
    """Services used to manage blacklisted users."""

    blacklisted_ids: list[int]

    def __init__(self, bot: "Vindex") -> None:
        self.bot = bot
        super().__init__()

    async def add_to_blacklist(self, author: discord.abc.User, user_id: int, reason: str) -> bool:
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
            return False
        user = await self.bot.database.user.find_unique(where={"id": user_id})
        if not user:
            await self.bot.database.user.create({"id": user_id})
        await self.bot.database.blacklist.upsert(
            where={"id": user_id},
            data={
                "create": {
                    "id": user_id,
                    "reason": reason,
                    "active": True,
                    "blacklistedById": author.id,
                },
                "update": {
                    "reason": reason,
                    "active": True,
                    "blacklistedBy": {
                        "connect": {
                            "id": author.id,
                        },
                    },
                },
            },
        )
        self.blacklisted_ids.append(user_id)
        return True

    async def remove_from_blacklist(
        self, author: discord.abc.User, user_id: int, reason: str
    ) -> bool:
        """Remove an user from the blacklist.

        Parameters
        ----------
        author : discord.abc.User
            The user who is removing the user from the blacklist.
        user_id : int
            The id of the user to remove from the blacklist.
        reason : str
            The reason for removing the user from the blacklist.

        Returns
        -------
        bool
            Whether the user was removed from the blacklist or not.
        """
        if not self.is_blacklisted(user_id):
            return False
        await self.bot.database.blacklist.update(
            where={"id": user_id},
            data={
                "reason": reason,
                "active": False,
                "blacklistedBy": {
                    "connect": {
                        "id": author.id,
                    }
                },
            },
        )
        self.blacklisted_ids.remove(user_id)
        return True

    async def get_blacklist(self, user_id: int) -> prisma.models.Blacklist | None:
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
        return await self.bot.database.blacklist.find_unique(
            where={"id": user_id}, include={"blacklistedBy": True, "user": True}
        )

    def is_blacklisted(self, user_id: int) -> bool:
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
        if user_id in self.blacklisted_ids:
            return True
        return False

    async def setup(self) -> None:
        """Prepare the service."""
        self.blacklisted_ids = [
            user.id
            for user in await self.bot.database.user.find_many(
                where={
                    "blacklist": {
                        "is": {
                            "active": True,
                        }
                    }
                }
            )
        ]
