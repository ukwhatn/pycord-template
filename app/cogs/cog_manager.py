import pathlib
from typing import List

import discord
from discord.commands import Option, slash_command
from discord.ext import commands

from core import get_settings


class CogManager(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.settings = get_settings()

    async def autocomplete_loaded_cog_names(
        self, ctx: discord.ApplicationContext
    ) -> List[str]:
        """現在ロードされているCog名の自動補完（モジュール名で返す）"""
        # Cogクラス名からモジュール名を逆引きするマッピング
        cog_to_module = {}
        for module_name, extension in self.bot.extensions.items():
            if module_name.startswith("cogs."):
                file_name = module_name.removeprefix("cogs.")
                for cog_class_name in self.bot.cogs.keys():
                    cog_obj = self.bot.cogs[cog_class_name]
                    if cog_obj.__module__ == module_name:
                        cog_to_module[cog_class_name] = file_name
                        break

        # ユーザー入力に基づいてフィルタリング
        module_names = list(cog_to_module.values())
        return [
            name for name in module_names if name.lower().startswith(ctx.value.lower())
        ]

    async def autocomplete_all_cogfile_names(
        self, ctx: discord.ApplicationContext
    ) -> List[str]:
        """利用可能な全Cogファイル名の自動補完"""

        # 現在のファイルからcogsディレクトリのパスを取得
        cogs_dir = pathlib.Path(__file__).parent
        cog_files = [
            f.stem
            for f in cogs_dir.glob("*.py")
            if f.name not in ["__init__.py", "template.py"]
        ]

        return [
            name for name in cog_files if name.lower().startswith(ctx.value.lower())
        ]

    def _create_success_embed(self, title: str, description: str) -> discord.Embed:
        """成功時のEmbed作成"""
        embed = discord.Embed(
            title=title, description=description, color=discord.Color.green()
        )
        return embed

    def _create_error_embed(
        self, title: str, description: str, error: str = None
    ) -> discord.Embed:
        """エラー時のEmbed作成"""
        embed = discord.Embed(
            title=title, description=description, color=discord.Color.red()
        )
        if error:
            embed.add_field(name="エラー詳細", value=f"```{error}```", inline=False)
        return embed

    @slash_command(name="reload", description="指定したCogをリロードします")
    @commands.is_owner()
    async def reload(
        self,
        ctx: discord.ApplicationContext,
        modulename: Option(
            str, "リロードするCog名", autocomplete=autocomplete_loaded_cog_names
        ),
    ) -> None:
        await ctx.response.defer(ephemeral=True)

        # モジュール名がロードされているかチェック
        module_full_name = f"cogs.{modulename}"
        if module_full_name not in self.bot.extensions:
            embed = self._create_error_embed(
                "リロード失敗", f"Cog `{modulename}` は現在ロードされていません"
            )
            await ctx.followup.send(embed=embed)
            return

        try:
            self.bot.reload_extension(f"cogs.{modulename}")
            embed = self._create_success_embed(
                "リロード完了", f"Cog `{modulename}` を正常にリロードしました"
            )
            await ctx.followup.send(embed=embed)
        except Exception as e:
            embed = self._create_error_embed(
                "リロード失敗", f"Cog `{modulename}` のリロードに失敗しました", str(e)
            )
            await ctx.followup.send(embed=embed)

    @slash_command(name="load", description="指定したCogをロードします")
    @commands.is_owner()
    async def load(
        self,
        ctx: discord.ApplicationContext,
        modulename: Option(
            str, "ロードするCog名", autocomplete=autocomplete_all_cogfile_names
        ),
    ) -> None:
        await ctx.response.defer(ephemeral=True)

        # モジュール名が既にロードされているかチェック
        module_full_name = f"cogs.{modulename}"
        if module_full_name in self.bot.extensions:
            embed = self._create_error_embed(
                "ロード失敗", f"Cog `{modulename}` は既にロードされています"
            )
            await ctx.followup.send(embed=embed)
            return

        try:
            self.bot.load_extension(f"cogs.{modulename}")
            embed = self._create_success_embed(
                "ロード完了", f"Cog `{modulename}` を正常にロードしました"
            )
            await ctx.followup.send(embed=embed)
        except Exception as e:
            embed = self._create_error_embed(
                "ロード失敗", f"Cog `{modulename}` のロードに失敗しました", str(e)
            )
            await ctx.followup.send(embed=embed)

    @slash_command(name="unload", description="指定したCogをアンロードします")
    @commands.is_owner()
    async def unload(
        self,
        ctx: discord.ApplicationContext,
        modulename: Option(
            str, "アンロードするCog名", autocomplete=autocomplete_loaded_cog_names
        ),
    ) -> None:
        await ctx.response.defer(ephemeral=True)

        # モジュール名がロードされているかチェック
        module_full_name = f"cogs.{modulename}"
        if module_full_name not in self.bot.extensions:
            embed = self._create_error_embed(
                "アンロード失敗", f"Cog `{modulename}` は現在ロードされていません"
            )
            await ctx.followup.send(embed=embed)
            return

        if modulename == "cog_manager":
            embed = self._create_error_embed(
                "アンロード失敗", "CogManager自体をアンロードすることはできません"
            )
            await ctx.followup.send(embed=embed)
            return

        try:
            self.bot.unload_extension(f"cogs.{modulename}")
            embed = self._create_success_embed(
                "アンロード完了", f"Cog `{modulename}` を正常にアンロードしました"
            )
            await ctx.followup.send(embed=embed)
        except Exception as e:
            embed = self._create_error_embed(
                "アンロード失敗",
                f"Cog `{modulename}` のアンロードに失敗しました",
                str(e),
            )
            await ctx.followup.send(embed=embed)

    @slash_command(name="cogs", description="現在ロードされているCogの一覧を表示します")
    @commands.is_owner()
    async def list_cogs(self, ctx: discord.ApplicationContext) -> None:
        await ctx.response.defer(ephemeral=True)

        # ロード済みCogのモジュール名を取得
        loaded_modules = []
        for module_name in self.bot.extensions.keys():
            if module_name.startswith("cogs."):
                loaded_modules.append(module_name.removeprefix("cogs."))

        # 利用可能なCogファイル一覧
        cogs_dir = pathlib.Path(__file__).parent
        available_files = [
            f.stem
            for f in cogs_dir.glob("*.py")
            if f.name not in ["__init__.py", "template.py"]
        ]

        unloaded_cogs = [cog for cog in available_files if cog not in loaded_modules]

        embed = discord.Embed(title="Cog管理状況", color=discord.Color.blue())

        if loaded_modules:
            # クラス名も併記
            cog_info = []
            for module in sorted(loaded_modules):
                module_full = f"cogs.{module}"
                if module_full in self.bot.extensions:
                    # モジュールからCogクラス名を取得
                    for cog_name, cog_obj in self.bot.cogs.items():
                        if cog_obj.__module__ == module_full:
                            cog_info.append(f"• {module} ({cog_name})")
                            break
                    else:
                        cog_info.append(f"• {module}")
                else:
                    cog_info.append(f"• {module}")

            embed.add_field(
                name=f"ロード済み ({len(loaded_modules)})",
                value="```\n" + "\n".join(cog_info) + "\n```",
                inline=False,
            )

        if unloaded_cogs:
            embed.add_field(
                name=f"未ロード ({len(unloaded_cogs)})",
                value="```\n"
                + "\n".join(f"• {cog}" for cog in sorted(unloaded_cogs))
                + "\n```",
                inline=False,
            )

        if not loaded_modules and not unloaded_cogs:
            embed.description = "利用可能なCogが見つかりません"

        await ctx.followup.send(embed=embed)


def setup(bot: commands.Bot) -> None:
    return bot.add_cog(CogManager(bot))
