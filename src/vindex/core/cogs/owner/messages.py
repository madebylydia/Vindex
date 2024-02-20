import typing

import discord

if typing.TYPE_CHECKING:
    from vindex.core.services.cogs_manager import ReturnLoad, ReturnReload, ReturnUnload


class LoadUnloadReloadEmbed(discord.Embed):
    """Custom embed object to generate an embed based of a specified typed dict for loading,
    reloading, and unloading cogs.
    """

    def __init__(self, *, data: "ReturnLoad | ReturnUnload | ReturnReload"):
        if data.get("already_loaded") or data.get("not_loaded"):
            color = discord.Color.blue()
        elif data["not_found"]:
            color = discord.Color.orange()
        elif data.get("failed"):
            color = discord.Color.red()
        else:
            color = discord.Color.green()

        super().__init__(title="Completed", color=color)

        if failed := data.get("failed"):
            self.add_field(name="Failed", value="\n".join(failed))
        if not_found := data.get("not_found"):
            self.add_field(name="Not Found", value="\n".join(not_found))
        if already_loaded := data.get("already_loaded"):
            self.add_field(name="Already Loaded", value="\n".join(already_loaded))
        if not_loaded := data.get("not_loaded"):
            self.add_field(name="Not Loaded", value="\n".join(not_loaded))
        if loaded := data.get("loaded"):
            self.add_field(name="Loaded", value="\n".join(loaded))
        if reloaded := data.get("reloaded"):
            self.add_field(name="Reloaded", value="\n".join(reloaded))
        if unloaded := data.get("unloaded"):
            self.add_field(name="Unloaded", value="\n".join(unloaded))
