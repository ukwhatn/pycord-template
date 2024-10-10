import asyncio
import logging

import discord
import sentry_sdk
from discord.ext import commands

from config import bot_config
from util.healthcheck import start_server

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s][%(levelname)s] %(message)s"
)

if bot_config.SENTRY_DSN is not None and bot_config.SENTRY_DSN != "":
    sentry_sdk.init(
        dsn=bot_config.SENTRY_DSN,
        traces_sample_rate=1.0
    )

if bot_config.TOKEN is None or bot_config.TOKEN == "":
    logging.error("TOKEN is not set.")
    exit(0)


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @commands.Cog.listener()
    async def on_ready(self):
        await asyncio.create_task(start_server(self, 8080, 1.0))


# bot init
bot = Bot(help_command=None,
          case_insensitive=True,
          activity=discord.Game("©Yuki Watanabe"),
          intents=discord.Intents.all()
          )

bot.load_extension("cogs.Admin")
bot.load_extension("cogs.CogManager")

bot.run(bot_config.TOKEN)
