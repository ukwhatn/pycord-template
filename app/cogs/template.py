import logging

from discord.ext import commands

from core import get_settings


class Template(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings = get_settings()
        self.logger = logging.getLogger("discord")


def setup(bot):
    return bot.add_cog(Template(bot))
