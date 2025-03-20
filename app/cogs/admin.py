import logging
import platform
import re
import sys
import traceback
from datetime import datetime
from typing import Optional, Type, Any

import discord
import psutil
from discord import slash_command
from discord.ext import commands

from core import get_settings
from utils import DiscordUtil


class Admin(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.settings = get_settings()
        self.logger = logging.getLogger("discord")

        # グローバルエラーハンドラーを設定
        bot.on_error = self.on_error

    @commands.Cog.listener(name="on_ready")
    async def on_ready(self):
        # 起動時刻を記録
        self.bot.start_time = discord.utils.utcnow()

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
            context_info=None,
        )

    @commands.Cog.listener()
    async def on_application_command_error(
        self, ctx: discord.ApplicationContext, error: discord.DiscordException
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
            "User": f"{ctx.author} ({ctx.author.id})",
        }

        # ギルド情報を追加（DMの場合は追加しない）
        if ctx.guild:
            context_info["Guild"] = f"{ctx.guild.name} ({ctx.guild.id})"
            context_info["Channel"] = f"{ctx.channel.name} ({ctx.channel.id})"

        # エラー通知
        await self._notify_error(
            error_type=type(original_error),
            error=original_error,
            traceback_obj=original_error.__traceback__,
            title=f"Command Error: {ctx.command}",
            context_info=context_info,
        )

    async def _notify_error(
        self,
        error_type: Type[Exception],
        error: Exception,
        traceback_obj: Any,
        title: str,
        context_info: Optional[dict] = None,
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

            error_message = (
                f"```py\n{traceback_text}\n{error_type.__name__}: {error}\n```"
            )

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
                    error_message[i : i + 1024]
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

    @slash_command(name="status", description="ボットのステータスを確認します")
    @commands.is_owner()
    async def status(self, ctx: discord.ApplicationContext):
        """ボットのステータス情報を表示します"""
        await ctx.defer(ephemeral=True)

        # 基本情報を収集
        uptime = (
            discord.utils.utcnow() - self.bot.start_time
            if hasattr(self.bot, "start_time")
            else None
        )
        uptime_str = str(uptime).split(".")[0] if uptime else "Unknown"

        # サーバー数、ユーザー数などの統計
        guilds_count = len(self.bot.guilds)
        users_count = sum(g.member_count for g in self.bot.guilds)

        # システム情報
        process = psutil.Process()
        memory_usage = process.memory_info().rss / (1024 * 1024)  # MB単位

        # Embedを作成
        embed = discord.Embed(
            title="Bot Status",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow(),
        )

        # 基本情報
        embed.add_field(
            name="Bot",
            value=f"{self.bot.user.name} (`{self.bot.user.id}`)",
            inline=False,
        )
        embed.add_field(name="Environment", value=self.settings.ENV_MODE, inline=True)
        embed.add_field(name="Uptime", value=uptime_str, inline=True)

        # 統計情報
        embed.add_field(name="Guilds", value=str(guilds_count), inline=True)
        embed.add_field(name="Users", value=str(users_count), inline=True)
        embed.add_field(
            name="Commands", value=str(len(self.bot.application_commands)), inline=True
        )

        # システム情報
        embed.add_field(name="Python", value=platform.python_version(), inline=True)
        embed.add_field(name="Discord.py", value=discord.__version__, inline=True)
        embed.add_field(name="Memory", value=f"{memory_usage:.2f} MB", inline=True)

        # フッター
        embed.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url
        )

        await ctx.respond(embed=embed)

    async def autocomplete_guilds(self, ctx: discord.AutocompleteContext):
        guilds = [
            f"{guild.name}({guild.id}/{guild.owner.display_name})"
            for guild in self.bot.guilds
        ]
        return [value for value in guilds if value.startswith(ctx.value)]

    @slash_command(
        name="leave_from_guild", description="指定したサーバーからボットを退出させます"
    )
    @commands.is_owner()
    async def leave_from_guild(
        self,
        ctx: discord.ApplicationContext,
        guild: discord.Option(
            str,
            "サーバー名",
            autocomplete=autocomplete_guilds,
        ),
    ):
        """指定したサーバーからボットを退出させます"""
        _, g_id, _ = re.match(r"(.+)\((\d+)/(.+)\)", guild).groups()
        guild = self.bot.get_guild(int(g_id))
        if guild is None:
            await ctx.respond("サーバーが見つかりませんでした", ephemeral=True)

        try:
            await guild.leave()
            await ctx.respond(f"{guild.name} から退出しました", ephemeral=True)
        except Exception as e:
            await ctx.respond(f"エラーが発生しました: {e}", ephemeral=True)


def setup(bot):
    return bot.add_cog(Admin(bot))
