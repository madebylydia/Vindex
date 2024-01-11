import typing

import discord
from discord.ext import commands

from vindex.core.checks import is_bot_mod
from vindex.core.core_types import Context
from vindex.core.i18n import Translator
from vindex.core.ui.formatting import inline

if typing.TYPE_CHECKING:
    from vindex.core.bot import Vindex


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
    async def cmd_admin_blacklist(self, ctx: Context):
        """Blacklist management."""

    @cmd_admin_blacklist.command(name="add")
    async def cmd_blacklist_add(
        self, ctx: Context, user_or_id: discord.User | int, *, reason: str
    ):
        """Add a user to the blacklist."""
        user_id = user_or_id.id if isinstance(user_or_id, discord.User) else user_or_id

        if user_id == ctx.author.id:
            await ctx.send(_("Self-harm is not tolerated. Shall you not block yourself!"))
            return
        if user_id in self.bot.bot_mods:
            await ctx.send(_("You cannot block a bot moderator."))
            return
        owners_ids = self.bot.owner_ids or [self.bot.owner_id]
        if user_id in owners_ids:
            await ctx.send(_("You cannot block bot owner(s)."))
            return

        result = await self.bot.services.blacklist.add_to_blacklist(ctx.author, user_id, reason)
        if result:
            await ctx.tick()
        else:
            await ctx.send(_("User is already blacklisted."))

    @cmd_admin_blacklist.command(name="remove")
    async def cmd_blacklist_remove(
        self, ctx: Context, user_or_id: discord.User | int, *, reason: str
    ):
        """Remove a user from the blacklist."""
        user_id = user_or_id.id if isinstance(user_or_id, discord.User) else user_or_id
        result = await self.bot.services.blacklist.remove_from_blacklist(
            ctx.author, user_id, reason
        )
        if result:
            await ctx.tick()
        else:
            await ctx.send(_("User is not blacklisted."))

    @cmd_admin_blacklist.command(name="check")
    async def cmd_blacklist_check(self, ctx: Context, user_or_id: discord.User | int):
        """Check if a user is blacklisted."""
        user_id = user_or_id.id if isinstance(user_or_id, discord.User) else user_or_id
        result = await self.bot.services.blacklist.get_blacklist(user_id)
        if result:
            # Fetched by get_blacklist
            assert result.user and result.blacklistedBy

            fetched_user = self.bot.get_user(result.id)
            fetched_author = self.bot.get_user(result.blacklistedBy.id)

            embed = discord.Embed(
                title=_("Blacklisted") if result.active else _("Not Blacklisted"),
                color=discord.Color.red() if result.active else discord.Color.green(),
            )
            embed.add_field(name=_("User ID"), value=inline(str(result.user.id)))
            if fetched_user:
                embed.set_thumbnail(url=fetched_user.display_avatar.url)
                if fetched_user.banner:
                    embed.set_image(url=fetched_user.banner.url)
                embed.add_field(
                    name=_("Known as"),
                    value=f"- {fetched_user.display_name}\n- {fetched_user.mention}",
                )

            embed.add_field(name=_("Blacklisted by"), value=inline(str(result.blacklistedBy.id)))
            if fetched_author:
                embed.set_footer(
                    text=_("By {user} - Update: {update}").format(
                        user=fetched_author.display_name, update=str(result.updatedAt)
                    ),
                    icon_url=fetched_author.display_avatar.url,
                )
            embed.add_field(name=_("Reason"), value=result.reason)
            embed.add_field(name=_("First blacklist data"), value=inline(str(result.createdAt)))

            await ctx.send(embed=embed)
        else:
            await ctx.send(_("This user is not blacklisted."))
