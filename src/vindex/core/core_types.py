import collections.abc
import typing

import discord
from discord.ext import commands
from discord.utils import MISSING as MISSING  # pylint: disable=unused-import

import prisma

if typing.TYPE_CHECKING:
    import os
    import pathlib

    from vindex.core.bot import Vindex


class SendMethodDict(typing.TypedDict):
    """Typed dict for reusability of the "send" method if required."""

    content: typing.NotRequired[str]
    embeds: typing.NotRequired[collections.abc.Sequence[discord.Embed]]
    files: typing.NotRequired[collections.abc.Sequence[discord.File]]
    stickers: typing.NotRequired[
        collections.abc.Sequence[discord.GuildSticker | discord.StickerItem]
    ]
    delete_after: typing.NotRequired[float]
    nonce: typing.NotRequired[str | int]
    allowed_mentions: typing.NotRequired[discord.AllowedMentions]
    reference: typing.NotRequired[
        discord.Message | discord.MessageReference | discord.PartialMessage
    ]
    mention_author: typing.NotRequired[bool]
    view: typing.NotRequired[discord.ui.View]
    suppress_embeds: typing.NotRequired[bool]
    silent: typing.NotRequired[bool]


BOT_COLOR = discord.Color.from_rgb(72, 184, 150)


class Context(commands.Context["Vindex"]):
    """Vindex's implementation of :py:class:`discord.ext.commands.Context`.

    Implements all methods of :py:class:`discord.ext.commands.Context` and adds
    some extra properties and methods.
    """

    @property
    def db(self) -> prisma.Prisma:
        """Return the database instance connected to the bot."""
        return self.bot.database

    @property
    def color(self) -> discord.Color:
        """Return the color used for embeds."""
        return BOT_COLOR

    async def tick(self, *, to_message: discord.Message | None = None) -> bool:
        """Add a tick reaction to the message.

        Parameters
        ----------
        to_message : Optional, :py:class:`discord.Message`
            The message to react to.
            If none, the context's message will be reacted to.

        Returns
        -------
        :py:class:`bool`
            Whether the reaction was successful.
        """
        return await self.try_react_with("✅", to_message=to_message)

    async def try_react_with(
        self, emoji: "discord.message.EmojiInputType", *, to_message: discord.Message | None = None
    ) -> bool:
        """Attempt to react to the context message.

        Parameters
        ----------
        emoji : :py:class:`discord.message.EmojiInputType`
            The emoji to react with.
        to_message : Optional, :py:class:`discord.Message`
            The message to react to.
            If none, the context's message will be reacted to.

        Returns
        -------
        :py:class:`bool`
            Whether the reaction was successful.
        """
        message = to_message or self.message
        try:
            await message.add_reaction(emoji)
        except (discord.HTTPException, discord.Forbidden):
            return False
        return True


if typing.TYPE_CHECKING:

    class GuildContext(commands.Context["Vindex"]):
        """Context used for commands ran in a guild. Same as Context."""

        @discord.utils.cached_property
        def author(self) -> discord.Member:  # pyright: ignore[reportIncompatibleVariableOverride]
            ...

        @discord.utils.cached_property
        def me(self) -> discord.Member:  # pyright: ignore[reportIncompatibleVariableOverride]
            ...

        @discord.utils.cached_property
        def channel(  # pyright: ignore[reportIncompatibleVariableOverride]
            self,
        ) -> discord.TextChannel | discord.VoiceChannel | discord.StageChannel | discord.Thread:
            ...

        @discord.utils.cached_property
        def guild(self) -> discord.Guild:  # pyright: ignore[reportIncompatibleVariableOverride]
            ...

    class DMContext(commands.Context["Vindex"]):
        """Context used for commands ran in private messages. Same as Context."""

        @discord.utils.cached_property
        def author(self) -> discord.User:  # pyright: ignore[reportIncompatibleVariableOverride]
            ...

        @discord.utils.cached_property
        def me(self) -> discord.ClientUser:  # pyright: ignore[reportIncompatibleVariableOverride]
            ...

        @discord.utils.cached_property
        def channel(  # pyright: ignore[reportIncompatibleVariableOverride]
            self,
        ) -> discord.DMChannel:
            ...

        @discord.utils.cached_property
        def guild(self) -> None:  # pyright: ignore[reportIncompatibleVariableOverride]
            ...

else:
    type GuildContext = Context
    type DMContext = Context

type StrPathOrPath = "str | pathlib.Path | os.PathLike[str]"
