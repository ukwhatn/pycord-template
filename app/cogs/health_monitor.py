import logging
import threading
import time

from discord.ext import commands

logger = logging.getLogger("discord")


class HealthMonitor(commands.Cog):
    """
    ボットの健全性をモニタリングし、ステータスファイルに記録する
    """

    def __init__(self, bot: commands.Bot, status_file="/tmp/bot_status.txt"):  # nosec B108
        self.bot = bot
        self.status_file = status_file
        self.running = True
        self.thread = threading.Thread(target=self._monitor, daemon=True)
        self.thread.start()
        logger.info(f"Health monitoring started with status file: {status_file}")

    def _monitor(self):
        """
        定期的にボットの状態をチェックしてファイルに書き込む
        """
        while self.running:
            self._update_status()
            time.sleep(30)

    def _update_status(self):
        """
        現在のボット状態をファイルに書き込む
        """
        try:
            is_healthy = self.bot.is_ready()
            status = "ready" if is_healthy else "not_ready"
            timestamp = int(time.time())

            with open(self.status_file, "w") as f:
                f.write(f"{status}:{timestamp}")
        except Exception as e:
            logger.error(f"Failed to update health status: {str(e)}")

    @commands.Cog.listener()
    async def on_connect(self):
        logger.info("Bot connected to Discord")
        self._update_status()

    @commands.Cog.listener()
    async def on_disconnect(self):
        logger.warning("Bot disconnected from Discord")
        self._update_status()

    @commands.Cog.listener()
    async def on_ready(self):
        self._update_status()

    def cog_unload(self):
        """
        コグアンロード時にモニタリングを停止する
        """
        self.running = False
        if self.thread.is_alive():
            self.thread.join(timeout=1.0)


def setup(bot):
    return bot.add_cog(HealthMonitor(bot))
