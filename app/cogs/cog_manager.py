import pathlib
from typing import Dict, List, Optional, Set

import discord
from discord.commands import Option, slash_command
from discord.ext import commands

from core import get_settings


class CogManager(commands.Cog):
    EXCLUDED_FILES: Set[str] = {"__init__.py", "template.py"}
    COG_MODULE_PREFIX = "cogs."

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.settings = get_settings()
        self._cogs_dir = pathlib.Path(__file__).parent

    def _get_full_module_name(self, module_name: str) -> str:
        """モジュール名からフルモジュール名を生成"""
        return f"{self.COG_MODULE_PREFIX}{module_name}"

    def _get_cog_module_mapping(self) -> Dict[str, str]:
        """Cogクラス名からモジュール名へのマッピングを取得"""
        mapping = {}
        for module_name in self.bot.extensions:
            if module_name.startswith(self.COG_MODULE_PREFIX):
                file_name = module_name.removeprefix(self.COG_MODULE_PREFIX)
                for cog_obj in self.bot.cogs.values():
                    if cog_obj.__module__ == module_name:
                        mapping[file_name] = cog_obj.__class__.__name__
                        break
        return mapping

    def _get_loaded_modules(self) -> List[str]:
        """ロード済みのCogモジュール名リストを取得"""
        return [
            module_name.removeprefix(self.COG_MODULE_PREFIX)
            for module_name in self.bot.extensions
            if module_name.startswith(self.COG_MODULE_PREFIX)
        ]

    def _get_available_cog_files(self) -> List[str]:
        """利用可能なCogファイル名リストを取得"""
        return [
            f.stem
            for f in self._cogs_dir.glob("*.py")
            if f.name not in self.EXCLUDED_FILES
        ]

    def _filter_by_input(self, items: List[str], user_input: str) -> List[str]:
        """ユーザー入力に基づいてアイテムをフィルタリング"""
        return [item for item in items if item.lower().startswith(user_input.lower())]

    async def autocomplete_loaded_cog_names(
        self, ctx: discord.ApplicationContext
    ) -> List[str]:
        """現在ロードされているCog名の自動補完"""
        loaded_modules = self._get_loaded_modules()
        return self._filter_by_input(loaded_modules, ctx.value)

    async def autocomplete_all_cogfile_names(
        self, ctx: discord.ApplicationContext
    ) -> List[str]:
        """利用可能な全Cogファイル名の自動補完"""
        available_files = self._get_available_cog_files()
        return self._filter_by_input(available_files, ctx.value)

    def _create_success_embed(self, title: str, description: str) -> discord.Embed:
        """成功時のEmbed作成"""
        return discord.Embed(
            title=title, description=description, color=discord.Color.green()
        )

    def _create_error_embed(
        self, title: str, description: str, error: Optional[str] = None
    ) -> discord.Embed:
        """エラー時のEmbed作成"""
        embed = discord.Embed(
            title=title, description=description, color=discord.Color.red()
        )
        if error:
            embed.add_field(name="エラー詳細", value=f"```{error}```", inline=False)
        return embed

    async def _handle_cog_operation(
        self,
        ctx: discord.ApplicationContext,
        modulename: str,
        operation: str,
        operation_func,
        success_message: str,
        error_message: str,
        pre_check=None,
    ) -> None:
        """Cog操作の共通処理"""
        await ctx.response.defer(ephemeral=True)

        module_full_name = self._get_full_module_name(modulename)

        if pre_check:
            error_embed = pre_check(module_full_name, modulename)
            if error_embed:
                await ctx.followup.send(embed=error_embed)
                return

        try:
            operation_func(module_full_name)
            embed = self._create_success_embed(operation, success_message)
            await ctx.followup.send(embed=embed)
        except Exception as e:
            embed = self._create_error_embed(operation, error_message, str(e))
            await ctx.followup.send(embed=embed)

    def _check_module_loaded(
        self, module_full_name: str, modulename: str
    ) -> Optional[discord.Embed]:
        """モジュールがロードされているかチェック"""
        if module_full_name not in self.bot.extensions:
            return self._create_error_embed(
                "操作失敗", f"Cog `{modulename}` は現在ロードされていません"
            )
        return None

    def _check_module_not_loaded(
        self, module_full_name: str, modulename: str
    ) -> Optional[discord.Embed]:
        """モジュールがロードされていないかチェック"""
        if module_full_name in self.bot.extensions:
            return self._create_error_embed(
                "操作失敗", f"Cog `{modulename}` は既にロードされています"
            )
        return None

    def _check_unload_restrictions(
        self, module_full_name: str, modulename: str
    ) -> Optional[discord.Embed]:
        """アンロード制限をチェック"""
        if module_full_name not in self.bot.extensions:
            return self._create_error_embed(
                "アンロード失敗", f"Cog `{modulename}` は現在ロードされていません"
            )
        if modulename == "cog_manager":
            return self._create_error_embed(
                "アンロード失敗", "CogManager自体をアンロードすることはできません"
            )
        return None

    @slash_command(name="reload", description="指定したCogをリロードします")
    @commands.is_owner()
    async def reload(
        self,
        ctx: discord.ApplicationContext,
        modulename: Option(
            str, "リロードするCog名", autocomplete=autocomplete_loaded_cog_names
        ),
    ) -> None:
        await self._handle_cog_operation(
            ctx=ctx,
            modulename=modulename,
            operation="リロード完了",
            operation_func=self.bot.reload_extension,
            success_message=f"Cog `{modulename}` を正常にリロードしました",
            error_message=f"Cog `{modulename}` のリロードに失敗しました",
            pre_check=self._check_module_loaded,
        )

    @slash_command(name="load", description="指定したCogをロードします")
    @commands.is_owner()
    async def load(
        self,
        ctx: discord.ApplicationContext,
        modulename: Option(
            str, "ロードするCog名", autocomplete=autocomplete_all_cogfile_names
        ),
    ) -> None:
        await self._handle_cog_operation(
            ctx=ctx,
            modulename=modulename,
            operation="ロード完了",
            operation_func=self.bot.load_extension,
            success_message=f"Cog `{modulename}` を正常にロードしました",
            error_message=f"Cog `{modulename}` のロードに失敗しました",
            pre_check=self._check_module_not_loaded,
        )

    @slash_command(name="unload", description="指定したCogをアンロードします")
    @commands.is_owner()
    async def unload(
        self,
        ctx: discord.ApplicationContext,
        modulename: Option(
            str, "アンロードするCog名", autocomplete=autocomplete_loaded_cog_names
        ),
    ) -> None:
        await self._handle_cog_operation(
            ctx=ctx,
            modulename=modulename,
            operation="アンロード完了",
            operation_func=self.bot.unload_extension,
            success_message=f"Cog `{modulename}` を正常にアンロードしました",
            error_message=f"Cog `{modulename}` のアンロードに失敗しました",
            pre_check=self._check_unload_restrictions,
        )

    def _create_cog_status_info(self, loaded_modules: List[str]) -> List[str]:
        """ロード済みCogの詳細情報を作成"""
        cog_mapping = self._get_cog_module_mapping()
        return [
            f"• {module} ({cog_mapping.get(module, 'Unknown')})"
            for module in sorted(loaded_modules)
        ]

    def _create_cog_status_embed(self) -> discord.Embed:
        """Cog状態表示用のEmbedを作成"""
        loaded_modules = self._get_loaded_modules()
        available_files = self._get_available_cog_files()
        unloaded_cogs = [cog for cog in available_files if cog not in loaded_modules]

        embed = discord.Embed(title="Cog管理状況", color=discord.Color.blue())

        if loaded_modules:
            cog_info = self._create_cog_status_info(loaded_modules)
            embed.add_field(
                name=f"ロード済み ({len(loaded_modules)})",
                value="```\n" + "\n".join(cog_info) + "\n```",
                inline=False,
            )

        if unloaded_cogs:
            unloaded_info = [f"• {cog}" for cog in sorted(unloaded_cogs)]
            embed.add_field(
                name=f"未ロード ({len(unloaded_cogs)})",
                value="```\n" + "\n".join(unloaded_info) + "\n```",
                inline=False,
            )

        if not loaded_modules and not unloaded_cogs:
            embed.description = "利用可能なCogが見つかりません"

        return embed

    @slash_command(name="cogs", description="現在ロードされているCogの一覧を表示します")
    @commands.is_owner()
    async def list_cogs(self, ctx: discord.ApplicationContext) -> None:
        await ctx.response.defer(ephemeral=True)
        embed = self._create_cog_status_embed()
        await ctx.followup.send(embed=embed)


def setup(bot: commands.Bot) -> None:
    return bot.add_cog(CogManager(bot))
