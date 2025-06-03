# py-cord DiscordBot テンプレート

[py-cord](https://github.com/Pycord-Development/pycord)を使用したDiscordBot開発用テンプレート。

## ✨ 機能

- **🔧 モジュラーアーキテクチャ**: 自動Cogローディングシステムによる整理されたコマンド構造
- **🗄️ データベース統合**: SQLAlchemy、PostgreSQL、Redis対応、マイグレーション管理
- **🐳 Docker対応**: Docker Composeによる完全なコンテナ化
- **⚡ 高速開発**: ホットリロード、自動フォーマット、包括的なツール群
- **🔒 セキュリティ重視**: BanditとSemgrepによる組み込みセキュリティスキャン
- **📊 監視機能**: Sentry統合によるエラートラッキングとシステム監視
- **🧪 コード品質**: Ruffによる自動リント、フォーマット、型チェック

## 🚀 クイックスタート

### 1. ボットを作成

1. このテンプレートを使用して新しいリポジトリを作成
2. リポジトリをクローン:
   ```bash
   git clone https://github.com/yourusername/your-bot-name.git
   cd your-bot-name
   ```

### 2. 環境セットアップ

```bash
# 環境ファイルをセットアップ
make envs:setup

# 依存関係をインストール
make dev:setup

# discord.envでボットトークンを設定
# 必要に応じて他の環境ファイルも編集
```

### 3. ボットを実行

**ローカル開発:**
```bash
cd app && python main.py
```

**Docker使用（推奨）:**
```bash
# データベースとRedisと一緒にボットを起動（不要ならfalseにする）
make up INCLUDE_DB=true INCLUDE_REDIS=true
```

ボットが起動しました！ 🎉

## 📚 ドキュメント

- **[開発ガイド](development.md)** - 機能構築、コマンド追加、データベース操作の完全ガイド
- **[クイックリファレンス](#クイックリファレンス)** - 開発に必要なコマンド一覧

## 🏗️ アーキテクチャ概要

```
app/
├── main.py              # エントリーポイント
├── cogs/                # cog（モジュール）群
├── core/config.py       # configの管理
├── db/                  # データベース層（モデル、スキーマ、CRUD）
└── utils/               # ユーティリティ関数とヘルパー
```

**主要機能:**
- **自動Cogローディング**: `cogs/`にPythonファイルを配置するだけで自動ロード
- **データベース層**: モデル、スキーマ、CRUD操作のクリーンな分離
- **設定システム**: Pydanticバリデーション付き環境ベース設定
- **エラーハンドリング**: 包括的なエラートラッキングとユーザーフレンドリーな応答

## 🛠️ 使用技術

- **[py-cord](https://github.com/Pycord-Development/pycord)** - モダンなDiscord APIラッパー
- **[SQLAlchemy](https://sqlalchemy.org/)** - マイグレーション対応データベースORM
- **[Pydantic](https://pydantic.dev/)** - データバリデーションと設定管理
- **[uv](https://github.com/astral-sh/uv)** - Pythonパッケージ管理
- **[Ruff](https://github.com/astral-sh/ruff)** - 超高速リントとフォーマット

## クイックリファレンス

### 必須コマンド

```bash
# 開発
make dev:setup          # 全依存関係をインストール
make envs:setup         # テンプレートから環境ファイルを作成

# コード品質
make format            # Ruffでコードをフォーマット
make lint              # コード品質をチェック
make security:scan     # セキュリティ分析を実行

# Docker操作
make up                # ボットコンテナを起動
make up INCLUDE_DB=true # データベース付きで起動
make logs              # コンテナログを表示
make down              # 全コンテナを停止

# データベース
make db:migrate        # データベースマイグレーションを適用
make db:revision:create NAME="説明" # 新しいマイグレーションを作成
```

### 機能追加

1. **Cogを作成**: `app/cogs/template.py`を`app/cogs/your_feature.py`にコピー
2. **コマンド追加**: Discordスラッシュコマンドには`@slash_command`デコレータを使用
3. **データベースモデル**: `app/db/models/`で自動リレーションハンドリング付きで定義
4. **テスト**: 開発中は`/reload your_feature`でホットリロード

各側面の詳細なチュートリアルは[開発ガイド](development.md)を参照してください。

## 🤝 コントリビューション

1. リポジトリをフォーク
2. 機能ブランチを作成
3. 変更を加える
4. テストとリントを実行: `make lint && make security:scan`
5. プルリクエストを送信

## 📄 ライセンス

このテンプレートはオープンソースで、[MITライセンス](LICENSE)の下で利用可能です。
