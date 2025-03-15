import logging
import sys
import traceback
from datetime import datetime
from typing import Optional, Type, Any

import discord
from discord.ext import commands

from core import get_settings
from utils import DiscordUtil


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings = get_settings()
        self.logger = logging.getLogger("discord")

        # グローバルエラーハンドラーを設定
        bot.on_error = self.on_error

    @commands.Cog.listener(name="on_ready")
    async def on_ready(self):
        if self.settings.is_production:
            await DiscordUtil.notify_to_owner(
                self.bot,
                f"{self.bot.user.name} is ready on {self.settings.ENV_MODE} mode",
            )
        else:
            self.logger.info(
                f"{self.bot.user.name} is started on {self.settings.ENV_MODE} mode"
            )

    async def on_error(self, event, *args, **kwargs):
        """
        グローバルなイベントエラーハンドラー
        通常のコマンドエラーではなく、イベント処理中のエラーをキャッチする
        """
        error_type, error, error_traceback = sys.exc_info()

        # エラーをログに記録
        self.logger.error(f"Error in {event}: {error}")
        self.logger.error(
            "".join(traceback.format_exception(error_type, error, error_traceback))
        )

        # エラー通知
        await self._notify_error(
            error_type=error_type,
            error=error,
            traceback_obj=error_traceback,
            title=f"Error in {event}",
            context_info=None
        )

    @commands.Cog.listener()
    async def on_command_error(
            self,
            ctx: commands.Context,
            error
    ):
        """
        コマンド実行時のエラーハンドラー
        """
        # 元のエラーを取得（CommandInvokeErrorの場合）
        original_error = error
        if isinstance(error, commands.CommandInvokeError):
            original_error = error.original

        # エラーをログに記録
        self.logger.error(f"Command error in {ctx.command}: {original_error}")
        self.logger.error("".join(traceback.format_tb(original_error.__traceback__)))

        # コンテキスト情報を収集
        context_info = {
            "Command": f"{ctx.command}",
            "Channel": f"{ctx.channel.name} ({ctx.channel.id})",
            "User": f"{ctx.author} ({ctx.author.id})"
        }

        # ギルド情報を追加（DMの場合は追加しない）
        if ctx.guild:
            context_info["Guild"] = f"{ctx.guild.name} ({ctx.guild.id})"

        # エラー通知
        await self._notify_error(
            error_type=type(original_error),
            error=original_error,
            traceback_obj=original_error.__traceback__,
            title=f"Command Error: {ctx.command}",
            context_info=context_info
        )

    async def _notify_error(
        self,
        error_type: Type[Exception],
        error: Exception,
        traceback_obj: Any,
        title: str,
        context_info: Optional[dict] = None
    ):
        """
        エラーをログに記録し、ボットオーナーに通知する共通処理

        Args:
            error_type: エラーの型
            error: エラーオブジェクト
            traceback_obj: トレースバックオブジェクト
            title: 通知タイトル
            context_info: コンテキスト情報の辞書 (オプション)
        """
        # ボットが準備完了していない場合は通知しない
        if not self.bot.is_ready():
            return

        try:
            # トレースバックメッセージを生成
            if isinstance(traceback_obj, list):
                traceback_text = "".join(traceback_obj)
            else:
                traceback_text = "".join(traceback.format_tb(traceback_obj, limit=15))

            error_message = f"```py\n{traceback_text}\n{error_type.__name__}: {error}\n```"

            # エラー通知用Embedを作成
            embed = discord.Embed(
                title=title,
                description=str(error),
                color=discord.Color.red(),
                timestamp=datetime.now(),
            )

            # エラータイプを追加
            embed.add_field(name="Error Type", value=error_type.__name__, inline=False)

            # コンテキスト情報があれば追加
            if context_info:
                for key, value in context_info.items():
                    embed.add_field(name=key, value=value, inline=True)

            # トレースバックが長い場合は分割して追加
            if len(error_message) > 1024:
                chunks = [
                    error_message[i: i + 1024]
                    for i in range(0, len(error_message), 1024)
                ]
                for i, chunk in enumerate(chunks):
                    embed.add_field(
                        name=f"Traceback {i + 1}/{len(chunks)}",
                        value=chunk,
                        inline=False,
                    )
            else:
                embed.add_field(name="Traceback", value=error_message, inline=False)

            # オーナーにDM送信
            await DiscordUtil.send_dm_to_owner(
                self.bot, content="⚠️ **Bot Error Alert**", embed=embed
            )
        except Exception as e:
            self.logger.error(f"Failed to send error notification: {e}")


def setup(bot):
    return bot.add_cog(Admin(bot))
