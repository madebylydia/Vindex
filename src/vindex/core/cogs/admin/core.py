import typing

import discord
from discord.ext import commands

from vindex.core.checks import is_bot_mod
from vindex.core.i18n import Translator

from . import messages

if typing.TYPE_CHECKING:
    from vindex.core.bot import Vindex
    from vindex.core.core_types import Context


_ = Translator("Admin", __file__)


class Admin(commands.Cog):
    """The Admin cog allow to take administrative action on the bot internal functionnalities.
    Most especially used by bot moderators and the owner.
    """

    def __init__(self, bot: "Vindex") -> None:
        self.bot = bot
        super().__init__()

    @commands.group(name="blacklist")
    @is_bot_mod()
    async def cmd_admin_blacklist(self, ctx: "Context"):
        """Blacklist management."""
        if not ctx.subcommand_passed:
            await ctx.send_help(ctx.command)

    @cmd_admin_blacklist.command(name="add")
    async def cmd_blacklist_add(
        self, ctx: "Context", user_or_id: discord.User | int, *, reason: str
    ):
        """Add a user to the blacklist."""
        user_id = user_or_id.id if isinstance(user_or_id, discord.User) else user_or_id

        if user_id == ctx.author.id:
            await ctx.send(_("Buddy, I don't tolerate self-harm."))
            return
        if self.bot.is_bot_mod_id(user_id):
            await ctx.send(_("You cannot block a bot moderator."))
            return
        owners_ids = self.bot.owner_ids or [self.bot.owner_id]
        if user_id in owners_ids:
            await ctx.send(_("You cannot block bot owner(s)."))
            return

        result = await self.bot.services.blacklist.add_to_blacklist(ctx.author, user_id, reason)
        if result:
            await self.bot.core_notify(embeds=[await messages.blacklist_add(ctx, result)])
            await ctx.tick()
        else:
            await ctx.send(_("User is already blacklisted."))

    @cmd_admin_blacklist.command(name="remove")
    async def cmd_blacklist_remove(
        self, ctx: "Context", user_or_id: discord.User | int, *, reason: str
    ):
        """Remove a user from the blacklist."""
        user_id = user_or_id.id if isinstance(user_or_id, discord.User) else user_or_id

        if user_id == ctx.author.id:
            await ctx.send(_("I don't think I can let you do that, buddy."))
            return

        result = await self.bot.services.blacklist.remove_from_blacklist(user_id)
        if result:
            await self.bot.core_notify(
                embeds=[await messages.blacklist_remove(ctx, result, reason)]
            )
            await ctx.tick()
        else:
            await ctx.send(_("User is not blacklisted."))

    @cmd_admin_blacklist.command(name="check")
    async def cmd_blacklist_check(self, ctx: "Context", user_or_id: discord.User | int):
        """Check if a user is blacklisted."""
        user_id = user_or_id.id if isinstance(user_or_id, discord.User) else user_or_id
        result = await self.bot.services.blacklist.get_blacklist(user_id)
        if result:
            embed = await messages.blacklist_check(ctx, result)
            await ctx.send(embed=embed)
        else:
            await ctx.send(_("This user is not blacklisted."))
