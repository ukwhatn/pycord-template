from discord.ext import commands

from core import get_settings
from utils import DiscordUtil


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings = get_settings()

    @commands.Cog.listener(name="on_ready")
    async def on_ready(self):
        if self.settings.is_production:
            await DiscordUtil.notify_to_owner(
                self.bot,
                f"{self.bot.user.name} is ready on {self.settings.ENV_MODE} mode",
            )


def setup(bot):
    return bot.add_cog(Admin(bot))
