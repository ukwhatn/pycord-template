from datetime import datetime

import discord


class DiscordUtil:
    @staticmethod
    async def send_dm(bot: discord.Bot, to: discord.User, **kwargs):
        dm_channel = await to.create_dm()
        await dm_channel.send(**kwargs)

    @staticmethod
    async def send_dm_to_owner(bot: discord.Bot, **kwargs):
        owner_id = bot.owner_id
        if not owner_id:
            app_info = await bot.application_info()
            owner = app_info.owner
        else:
            owner = await bot.fetch_user(owner_id)
        await DiscordUtil.send_dm(bot, owner, **kwargs)

    @staticmethod
    async def notify_to_owner(bot: discord.Bot, message: str):
        await DiscordUtil.send_dm_to_owner(
            bot,
            content="Notification",
            embed=discord.Embed()
            .add_field(name="Status", value=message)
            .set_footer(text=str(datetime.now())),
        )
