import glob

import discord
from discord.commands import Option, slash_command
from discord.ext import commands

from core import get_settings


class CogManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings = get_settings()

    async def autocomplete_loaded_cog_names(
        self, ctx: discord.commands.context.ApplicationContext
    ):
        return [value for value in self.bot.cogs.keys() if value.startswith(ctx.value)]

    async def autocomplete_all_cogfile_names(
        self, ctx: discord.commands.context.ApplicationContext
    ):
        values = [
            cog.removeprefix("/app/cogs/").removesuffix(".py")
            for cog in glob.glob("/app/cogs/*.py")
        ]
        return [value for value in values if value.startswith(ctx.value)]

    @slash_command(name="reload", description="指定したCogをリロードします")
    @commands.is_owner()
    async def reload(
        self,
        ctx: discord.commands.context.ApplicationContext,
        modulename: Option(
            str, "provide cog name", autocomplete=autocomplete_loaded_cog_names
        ),
    ):
        await ctx.response.defer(ephemeral=True, invisible=False)
        try:
            self.bot.reload_extension(f"cogs.{modulename}")
            await ctx.respond(f":arrows_counterclockwise: Reloaded {modulename}")
        except Exception:
            await ctx.respond(f":exclamation: Failed to reload {modulename}")

    @slash_command(name="load", description="指定したCogをロードします")
    @commands.is_owner()
    async def load(
        self,
        ctx: discord.commands.context.ApplicationContext,
        modulename: Option(
            str, "provide cog name", autocomplete=autocomplete_all_cogfile_names
        ),
    ):
        msg = await ctx.respond(f":arrow_up: Loading {modulename}")
        try:
            self.bot.load_extension(f"cogs.{modulename}")
            await msg.edit_original_response(content=":thumbsup: Loaded")
        except Exception:
            await msg.edit_original_response(content=":exclamation: Failed")

    @slash_command(name="unload", description="指定したCogをアンロードします")
    @commands.is_owner()
    async def unload(
        self,
        ctx: discord.commands.context.ApplicationContext,
        modulename: Option(
            str, "provide cog name", autocomplete=autocomplete_loaded_cog_names
        ),
    ):
        await ctx.response.defer(ephemeral=True, invisible=False)
        try:
            self.bot.unload_extension(f"cogs.{modulename}")
            await ctx.respond(f":arrow_down: Unloaded {modulename}")
        except Exception:
            await ctx.respond(f":exclamation: Failed to unload {modulename}")


def setup(bot):
    return bot.add_cog(CogManager(bot))
