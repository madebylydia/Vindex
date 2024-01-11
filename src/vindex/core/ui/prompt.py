import types
import typing

import discord

from vindex.core.core_types import Context, SendMethodDict


class ConfirmView(discord.ui.View):
    """A custom view to ask for user's confirmation. To use inside an async context manager.
    This will require all the arguments passed to the send method.
    """

    ctx: Context
    message_parameters: SendMethodDict

    message: discord.Message | None

    value: bool | None

    def __init__(
        self,
        ctx: Context,
        *,
        timeout: float = 60.0,
        **message_parameters: typing.Unpack[SendMethodDict]
    ):
        super().__init__(timeout=timeout)
        self.value = None
        self.ctx = ctx
        self.message_parameters = message_parameters

    async def on_timeout(self) -> None:
        await self.disable()
        self.stop()

    async def __aenter__(self) -> bool | None:
        self.message = await self.ctx.send(
            **self.message_parameters, view=self
        )  # pyright: ignore[reportGeneralTypeIssues]
        await self.wait()
        await self.disable()
        self.stop()
        return self.value

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        value: BaseException | None,
        traceback: types.TracebackType | None,
    ):
        if not self.is_finished():
            await self.disable()
            print("stopped")
            self.stop()

    async def disable(self):
        for item in self.children:
            assert isinstance(item, discord.ui.Button)
            if (
                self.value is True
                and item.custom_id == "no"
                or self.value is False
                and item.custom_id == "yes"
            ):
                self.remove_item(item)
            else:
                item.disabled = True
        if self.message:
            await self.message.edit(view=self)

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green, custom_id="yes")
    async def yes(self, interaction: discord.Interaction, _: discord.ui.Button[typing.Self]):
        self.value = True
        await interaction.response.pong()
        self.stop()

    @discord.ui.button(label="No", style=discord.ButtonStyle.red, custom_id="no")
    async def no(self, interaction: discord.Interaction, _: discord.ui.Button[typing.Self]):
        self.value = False
        await interaction.response.defer()
        self.stop()
