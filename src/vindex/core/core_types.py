import typing

from discord.ext import commands

if typing.TYPE_CHECKING:
    import os
    import pathlib

    import discord

    from vindex.core.bot import Vindex

type Context = "commands.Context[Vindex]"

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
    GuildContext: Context = Context
    DMContext: Context = Context

type StrPathOrPath = "str | pathlib.Path | os.PathLike[str]"
