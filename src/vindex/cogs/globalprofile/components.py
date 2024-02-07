import logging
import typing

import discord
from discord.interactions import Interaction
from prisma.models import Profile

_log = logging.getLogger(__name__)


class ProfileBasicButton(discord.ui.Button["BasicComponent"]):
    profile: "Profile"

    def __init__(self, profile: "Profile"):
        self.profile = profile
        super().__init__(label="Basic info")

    async def callback(self, interaction: Interaction) -> typing.Any:
        return await interaction.response.send_modal(BasicComponent(self.profile))


class ProfileEditView(discord.ui.View):
    """A view that provide information about a profile."""

    profile: "Profile"

    def __init__(self, profile: "Profile", *, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.add_item(ProfileBasicButton(profile))


class ProfileComponent(discord.ui.Modal, title="Edit your Profile"):
    """A component used for showing and editing values of a profile."""

    profile: "Profile"

    def __init__(
        self,
        profile: "Profile",
        *,
        timeout: float | None = 180,
    ):
        self.profile = profile
        super().__init__(timeout=timeout)


class BasicComponent(ProfileComponent):
    """Profile-specific component to edit the basic informations of the profile."""

    color: discord.ui.TextInput["BasicComponent"]

    def __init__(self, profile: "Profile"):
        super().__init__(profile)
        self.add_item(discord.ui.TextInput(label="Color", placeholder="Color of your embed"))


class FieldsComponent(ProfileComponent):
    """Profile-specific component to edit the embed fields of the profile."""
