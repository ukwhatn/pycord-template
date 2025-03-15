import logging

import discord
import sentry_sdk
from discord.ext import commands

from core import get_settings

config = get_settings()

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s][%(levelname)s] %(message)s"
)
logger = logging.getLogger("discord")

if config.is_production and config.SENTRY_DSN is not None and config.SENTRY_DSN != "":
    logger.info("Sentry is enabled")
    sentry_sdk.init(dsn=config.SENTRY_DSN, traces_sample_rate=1.0)

if config.BOT_TOKEN is None or config.BOT_TOKEN == "":
    raise ValueError("BOT_TOKEN is not set")

# bot init
bot = commands.Bot(
    help_command=None,
    case_insensitive=True,
    activity=discord.Game("©ukwhatn"),
    intents=discord.Intents.all(),
)

cogs = ["admin", "cog_manager"]

for cog_name in cogs:
    bot.load_extension(f"cogs.{cog_name}")

bot.run(config.BOT_TOKEN)
