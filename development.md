# 開発ガイド

このガイドでは、pycord-templateを使用してDiscordボットを作成するための完全な開発ワークフローを説明します。

## 目次

1. [初期セットアップ](#初期セットアップ)
2. [開発環境](#開発環境)
3. [プロジェクト構造](#プロジェクト構造)
4. [Cogの作成](#cogの作成)
5. [スラッシュコマンドの追加](#スラッシュコマンドの追加)
6. [データベース操作](#データベース操作)
7. [設定管理](#設定管理)
8. [Docker開発](#docker開発)
9. [コード品質とテスト](#コード品質とテスト)

---

## 初期セットアップ

### 1. テンプレートからリポジトリを作成

1. テンプレートリポジトリにアクセス
2. "Use this template" → "Create a new repository"をクリック
3. リポジトリ名と設定を選択
4. 新しいリポジトリをクローン:
   ```bash
   git clone https://github.com/yourusername/your-bot-name.git
   cd your-bot-name
   ```

### 2. 環境セットアップ

1. **uv（Pythonパッケージマネージャー）をインストール**:
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # pipを使用する場合
   pip install uv
   ```

2. **環境ファイルをセットアップ**:
   ```bash
   make envs:setup
   ```
   これにより`envs/`ディレクトリのテンプレートから環境ファイルが作成されます。

3. **環境変数を設定**:
   - `discord.env`を編集 - DiscordボットトークンAを追加
   - `db.env`を編集 - データベース認証情報を設定
   - 必要に応じて他の`.env`ファイルも編集

4. **依存関係をインストール**:
   ```bash
   make dev:setup
   ```

---

## 開発環境

### ローカル開発（Dockerなし）

データベースなしでのシンプルなボット開発の場合:

```bash
# 依存関係をインストール
make dev:setup

# 環境変数を直接設定または.envファイルを使用
export BOT_TOKEN="your_discord_bot_token"
export ENV_MODE="development"

# ボットを実行
cd app && python main.py
```

### Docker開発（推奨）

データベースとRedisを含むフルスタック開発の場合:

```bash
# 全サービス（ボット、データベース、Redis）を起動
make up INCLUDE_DB=true INCLUDE_REDIS=true

# またはボットのみを起動
make up

# ログを確認
make logs

# サービスを停止
make down
```

### 開発コマンド

- `make lint` - コード品質をチェック
- `make format` - コードをフォーマット
- `make security:scan` - セキュリティスキャンを実行

---

## プロジェクト構造

```
app/
├── main.py              # ボットエントリーポイント
├── core/
│   ├── config.py        # 設定管理
├── cogs/                # Discordコマンドモジュール
│   ├── template.py      # 新しいCog用テンプレート（ロードされない）
│   ├── admin.py         # 管理者コマンド
│   ├── cog_manager.py   # Cog管理コマンド
│   └── health_monitor.py
├── db/                  # データベース層
│   ├── models/          # SQLAlchemyモデル
│   ├── schemas/         # Pydanticスキーマ
│   ├── crud/            # データベース操作
│   └── connection.py    # データベース接続
└── utils/               # ユーティリティモジュール
```

---

## Cogの作成

CogはDiscordコマンドとイベントリスナーを含むモジュラーコンポーネントです。

### 1. 新しいCogを作成

**テンプレートをコピー**:
```bash
cp app/cogs/template.py app/cogs/your_feature.py
```

### 2. 基本的なCog構造

```python
import logging
from discord.ext import commands
from core import get_settings

class YourFeature(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings = get_settings()
        self.logger = logging.getLogger("discord")

    # イベントリスナー
    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info("YourFeature cog is ready")

def setup(bot):
    return bot.add_cog(YourFeature(bot))
```

### 3. 自動ローディング

CogはボットStart時に`app/cogs/`ディレクトリから自動的にロードされます（`template.py`を除く）。ローディングロジックは`app/main.py:34-39`を参照してください。

### 4. Cog管理

実行時にCogを管理するための組み込みコマンドを使用:
- `/reload <cog_name>` - Cogをリロード
- `/load <cog_name>` - 新しいCogをロード
- `/unload <cog_name>` - Cogをアンロード

---

## スラッシュコマンドの追加

### 1. 基本的なスラッシュコマンド

```python
from discord import slash_command, Option
from discord.ext import commands

class YourFeature(commands.Cog):
    @slash_command(name="hello", description="誰かに挨拶する")
    async def hello(
        self, 
        ctx, 
        user: Option(str, "挨拶する相手", required=True)
    ):
        await ctx.respond(f"こんにちは、{user}さん！")
```

### 2. オプション付きコマンド

```python
@slash_command(name="setup", description="ユーザー設定をセットアップ")
async def setup(
    self,
    ctx,
    theme: Option(
        str,
        "テーマを選択",
        choices=["dark", "light", "auto"],
        required=True
    ),
    notifications: Option(
        bool,
        "通知を有効にする",
        required=False,
        default=True
    )
):
    await ctx.defer()  # 長時間実行されるコマンドの場合
    
    # ここにロジックを記述
    await ctx.respond(f"設定完了！テーマ: {theme}, 通知: {notifications}")
```

### 3. オートコンプリート

```python
async def autocomplete_items(self, ctx):
    # ユーザー入力に基づいて選択肢のリストを返す
    items = ["apple", "banana", "cherry"]
    return [item for item in items if item.startswith(ctx.value.lower())]

@slash_command(name="select", description="アイテムを選択")
async def select_item(
    self,
    ctx,
    item: Option(
        str,
        "アイテムを選択",
        autocomplete=autocomplete_items
    )
):
    await ctx.respond(f"選択されたアイテム: {item}")
```

### 4. エラーハンドリング

テンプレートには`admin.py`にグローバルエラーハンドリングが含まれていますが、コマンド固有のハンドリングも追加できます:

```python
@slash_command(name="divide", description="二つの数値を割る")
async def divide(self, ctx, a: int, b: int):
    try:
        result = a / b
        await ctx.respond(f"{a} ÷ {b} = {result}")
    except ZeroDivisionError:
        await ctx.respond("ゼロで割ることはできません！", ephemeral=True)
```

---

## データベース操作

### 1. モデルの作成

**`app/db/models/`で新しいモデルを定義**:

```python
# app/db/models/user.py
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from .base import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    
    discord_id: Mapped[int] = mapped_column(index=True, unique=True)
    username: Mapped[str] = mapped_column(String(100))
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    settings: Mapped[str] = mapped_column(String(1000), nullable=True)
```

### 2. スキーマの作成

**`app/db/schemas/`でPydanticスキーマを定義**:

```python
# app/db/schemas/user.py
from typing import Optional
from .base import BaseModelSchema, BaseSchema

class UserBase(BaseSchema):
    discord_id: int
    username: str
    is_premium: bool = False
    settings: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    discord_id: Optional[int] = None
    username: Optional[str] = None

class User(UserBase, BaseModelSchema):
    pass
```

### 3. CRUD操作の作成

**`app/db/crud/`でCRUDクラスを作成**:

```python
# app/db/crud/user.py
from typing import Optional
from sqlalchemy.orm import Session
from .base import CRUDBase
from db.models.user import User
from db.schemas.user import UserCreate, UserUpdate

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_discord_id(self, db: Session, discord_id: int) -> Optional[User]:
        return db.query(User).filter(User.discord_id == discord_id).first()
    
    def create_user(self, db: Session, discord_id: int, username: str) -> User:
        user_data = UserCreate(discord_id=discord_id, username=username)
        return self.create(db=db, obj_in=user_data)

user = CRUDUser(User)
```

### 4. CogでのデータベースNine

```python
from db.connection import get_db
from db.crud.user import user as user_crud

class YourFeature(commands.Cog):
    @slash_command(name="profile", description="プロフィールを表示")
    async def profile(self, ctx):
        db = next(get_db())
        try:
            # データベースからユーザーを取得
            db_user = user_crud.get_by_discord_id(db, ctx.author.id)
            
            if not db_user:
                # 新しいユーザーを作成
                db_user = user_crud.create_user(
                    db=db,
                    discord_id=ctx.author.id,
                    username=ctx.author.display_name
                )
            
            await ctx.respond(f"プロフィール: {db_user.username} (プレミアム: {db_user.is_premium})")
        
        finally:
            db.close()
```

### 5. データベースマイグレーション

```bash
# 新しいマイグレーションを作成
make db:revision:create NAME="add_user_table"

# マイグレーションを適用
make db:migrate

# 現在のマイグレーションを確認
make db:current

# マイグレーション履歴を表示
make db:history
```

---

## 設定管理

### 1. 環境変数

ボットは集約設定に`app/core/config.py`を使用します:

```python
# core/config.pyに新しい設定を追加
class Settings(BaseSettings):
    # 新しい設定
    API_KEY: str = ""
    FEATURE_ENABLED: bool = True
    MAX_ITEMS: int = 100
```

### 2. Cogでの設定使用

```python
class YourFeature(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings = get_settings()
        
    @slash_command(name="config", description="設定を表示")
    async def show_config(self, ctx):
        if self.settings.FEATURE_ENABLED:
            await ctx.respond(f"機能が有効です！最大アイテム数: {self.settings.MAX_ITEMS}")
        else:
            await ctx.respond("機能は無効です")
```

### 3. 環境固有の設定

`ENV_MODE`を設定して動作を制御:

```python
if self.settings.is_development:
    # 開発用コード
    self.logger.debug("デバッグ情報")

if self.settings.is_production:
    # 本番用コード
    await send_error_to_monitoring()
```

---

## Docker開発

### 1. データベースとの開発

```bash
# データベースとRedisと一緒に起動
make up INCLUDE_DB=true INCLUDE_REDIS=true

# Adminer（Webインターフェース）でデータベースにアクセス
# http://localhost:8080 にアクセス
# サーバー: db, ユーザー名/パスワード: db.envから

# データベースマイグレーションを実行
make db:migrate
```

### 2. Docker Composeプロファイル

`compose.yml`は起動するサービスを制御するためにプロファイルを使用:

- **app**: Discordボット（常に含まれる）
- **db**: PostgreSQLデータベース（`INCLUDE_DB=true`で含める）
- **redis**: Redisキャッシュ（`INCLUDE_REDIS=true`で含める）
- **dev**: Adminerなどの開発ツール

### 3. カスタムDockerコマンド

```bash
# 再ビルドして再起動
make reload

# 特定のサービスのログを表示
docker compose logs app -f

# コンテナ内でコマンドを実行
docker compose exec app python -c "from core import get_settings; print(get_settings().DATABASE_URI)"
```

---

## コード品質とテスト

### 1. コード品質ツール

```bash
# コードをリント（問題をチェック）
make lint

# リント問題を自動修正
make lint:fix

# コードをフォーマット
make format

# セキュリティスキャン
make security:scan
```

### 2. プリコミットワークフロー

コードをコミットする前に:

```bash
# フォーマットとリント
make format
make lint

# セキュリティスキャンを実行
make security:scan

# 変更をコミット
git add .
git commit -m "feat: 新機能を追加"
```

### 3. テストの追加（オプション）

テストを追加したい場合は、テストフレームワークを作成:

1. `pyproject.toml`にテスト依存関係を追加:
   ```toml
   dev = [
       "pytest>=7.0.0",
       "pytest-asyncio>=0.21.0",
       # ... 既存のdev依存関係
   ]
   ```

2. テスト構造を作成:
   ```
   tests/
   ├── conftest.py
   ├── test_cogs/
   └── test_db/
   ```

3. `Makefile`にテストコマンドを追加:
   ```makefile
   test:
   	uv run pytest tests/
   ```

---

## デプロイメントのヒント

### 1. 本番環境の環境変数

本番環境ファイルを作成:
- 強力なデータベースパスワードを使用
- `ENV_MODE=production`を設定
- エラー監視用にSentry DSNを設定
- 適切なログレベルを設定

### 2. データベースバックアップ

```bash
# データベースバックアップを作成
make db:dump:oneshot

# 利用可能なバックアップを一覧表示
make db:dump:list

# バックアップから復元
make db:dump:restore FILE=backup_filename.sql
```

### 3. 監視

- `/status`コマンドでボットステータスを確認
- `make logs`でログを監視
- 本番環境でのエラートラッキングにSentryをセットアップ

---

## 一般的なパターン

### 1. ユーザー権限チェック

```python
@slash_command(name="admin", description="管理者専用コマンド")
@commands.has_permissions(administrator=True)
async def admin_command(self, ctx):
    await ctx.respond("管理者コマンドが実行されました！")
```

### 2. データベースセッション管理

```python
async def database_operation(self, user_id: int):
    db = next(get_db())
    try:
        # データベース操作
        result = user_crud.get_by_discord_id(db, user_id)
        return result
    finally:
        db.close()
```

### 3. エラーハンドリングとロgging

```python
@slash_command(name="process", description="何かを処理する")
async def process(self, ctx):
    try:
        await ctx.defer()
        
        # 長時間実行される操作
        result = await self.complex_operation()
        
        await ctx.respond(f"完了: {result}")
        
    except Exception as e:
        self.logger.error(f"processコマンドでエラー: {e}")
        await ctx.respond("処理中にエラーが発生しました。", ephemeral=True)
```

この開発ガイドは、このテンプレートを使用してDiscordボットの構築を始めるのに役立ちます。各セクションでは、特定のニーズに適応できる実用的な例を提供しています。