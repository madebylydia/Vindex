import typing

import discord
from discord import app_commands
from discord.ext import commands
from prisma.models import Profile

from vindex.core.i18n import Translator
from vindex.core.ui.formatting import (as_str_timedelta, escape, inline,
                                       reduce_to)

if typing.TYPE_CHECKING:
    from vindex.core.bot import Vindex
    from vindex.core.core_types import Context


_ = Translator("GlobalProfile", __file__)


class GlobalProfile(commands.Cog):
    """Create and share a global profile across servers!

    This allows you to create a profile that is unique to you, and that will remain the same on
    all the servers you've joined.
    You can tell what modules you play, what level you're at, give a little description of
    yourself, and more!"""

    bot: "Vindex"

    def __init__(self, bot: "Vindex") -> None:
        self.bot = bot
        super().__init__()

    def build_profile(self, user: discord.abc.User, profile: Profile) -> discord.Embed:
        embed = discord.Embed(
            title=_("Profile of {user}").format(user=user.name),
            description=profile.description or _("No description"),
            color=discord.Color.blurple(),
        )

        update_delta = discord.utils.utcnow() - profile.updatedAt
        embed.set_footer(
            text=_("Last updated {date} ago").format(date=as_str_timedelta(update_delta))
        )
        return embed

    @commands.hybrid_group("profile")
    async def cmd_profile(self, ctx: "Context", *, user: discord.User | None = None):
        """Create and show your global profile!"""
        if ctx.subcommand_passed:
            return
        if user:
            profile = await Profile.prisma().find_unique(where={"id": user.id})
            if profile is None:
                return await ctx.send(_("This user does not have a profile yet!"))
            return await ctx.send(embed=self.build_profile(user, profile))

    @cmd_profile.command("get")
    @app_commands.describe(
        look_user="The user to get the profile of. If not given, it will default to your profile."
    )
    async def cmd_profile_get(self, ctx: "Context", *, look_user: discord.User | None = None):
        """Show the profile of an user."""
        user = look_user or ctx.author
        profile = await Profile.prisma().find_unique(where={"id": user.id})
        if profile is None:
            if user.id == ctx.author.id:
                return await ctx.send(_("You do not have a profile yet!"))
            return await ctx.send(_("This user does not have a profile yet!"))
        return await ctx.send(embed=self.build_profile(user, profile))

    @cmd_profile.group("set")
    async def cmd_profile_set(self, ctx: "Context"):
        """Set your global profile informations."""

    @cmd_profile_set.command("description")
    async def cmd_profile_set_description(self, ctx: "Context", *, description: str | None = None):
        """Set your profile description."""
        if description is None:
            profile = await Profile.prisma().find_unique(where={"id": ctx.author.id})
            if profile is None:
                return await ctx.send(_("You do not have a profile yet!"))
            if not profile.description:
                return await ctx.send(_("You do not have a description yet!"))
            return await ctx.send(
                _("Your current description is: {description}").format(
                    description=inline(escape(reduce_to(profile.description, 1500)))
                )
            )

        if len(description) > 2048:
            return await ctx.send(_("Your description cannot be longer than 2048 characters!"))
        await Profile.prisma().upsert(
            where={"id": ctx.author.id},
            data={
                "create": {
                    "user": {
                        "connect": {"id": ctx.author.id},
                        "create": {
                            "id": ctx.author.id,
                        },
                    },
                    "description": description,
                    "color": str(ctx.author.color),
                },
                "update": {"description": description},
            },
        )
        await ctx.send(
            _("Done! Your description is now: {description}").format(
                description=inline(escape(description))
            )
        )
