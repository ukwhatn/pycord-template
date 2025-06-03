# CLAUDE.md

このファイルは、Claude Code (claude.ai/code) がこのリポジトリのコードを扱う際のガイダンスを提供します。

## プロジェクト概要

py-cordで構築されたDiscordボットテンプレートで、プロダクション対応のDiscordボットの基盤を提供します。モジュラーアーキテクチャ、自動Cogロード、SQLAlchemyによるデータベース統合、Redis対応、包括的なDockerデプロイメントを使用します。

## ドキュメント構造

- **README.md**: ユーザー向けランディングページ（日本語）
- **development.md**: 完全な開発ガイド（日本語）- Cog作成、スラッシュコマンド、データベース操作、Docker開発
- **CLAUDE.md**: AI開発アシスタント向けプロジェクト情報

## 開発コマンド

### 環境セットアップ
- `make dev:setup` - uvを使用して全依存関係をインストール（discord, db, devグループ）
- `make envs:setup` - envs/ディレクトリから環境ファイルテンプレートをコピー

### コード品質
- `make lint` - Ruffリンターでコード品質をチェック
- `make lint:fix` - 自動修正付きでRuffを実行
- `make format` - Ruffフォーマッターでコードフォーマット

### Docker操作
- `make up` - 全コンテナをデタッチモードでビルド・起動
- `make down` - 全コンテナを停止
- `make reload` - コンテナを再ビルドして再起動
- `make logs` - コンテナログをフォロー
- `make ps` - 実行中のコンテナを表示

### データベース管理
- `make db:revision:create NAME="説明"` - 新しいAlembicマイグレーションを作成
- `make db:migrate` - データベースにマイグレーションを適用
- `make db:current` - 現在のマイグレーションリビジョンを表示
- `make db:history` - マイグレーション履歴を表示

### セキュリティスキャン
- `make security:scan` - 全セキュリティスキャンを実行（Bandit + Semgrep）
- `make security:scan:code` - Bandit静的解析を実行
- `make security:scan:sast` - Semgrepセキュリティ解析を実行

## アーキテクチャ

### コアコンポーネント
- **main.py**: `/app/cogs/`からの自動Cogローディング付きボットエントリーポイント（`template.py`を除く）
- **core/config.py**: Pydanticを使用した環境ベース設定の集約設定
- **cogs/**: 起動時に自動ロードされるDiscordコマンドモジュール
- **db/**: SQLAlchemyモデル、スキーマ、CRUD操作を含むデータベース層

### 設定システム
ボットはPydanticベースの設定システム（`core/config.py`）を使用し、以下をサポート:
- 環境固有設定（`ENV_MODE`による development/production/test）
- データベース接続管理（PostgreSQL）
- Redis統合
- Sentryエラートラッキング
- セキュリティヘッダーとCSPポリシー

### データベースアーキテクチャ
- **models/base.py**: 自動インクリメントIDと created_at/updated_at用の`TimeStampMixin`を持つ`BaseModel`を提供
- **models/**: `BaseModel`を継承するSQLAlchemyモデル定義
- **schemas/**: データバリデーション用Pydanticスキーマ
- **crud/**: ベースCRUD操作を持つデータベース操作層

### Cogシステム
- Cogは`template.py`を除く`/app/cogs/`から自動発見・ロード
- **cog_manager.py**: `/reload`, `/load`, `/unload`コマンドによるランタイムCog管理
- **health_monitor.py**: システム監視機能
- **admin.py**: 管理コマンド

### Docker設定
プロジェクトはマルチプロファイルDocker Compose設定を使用:
- **app**: メインDiscordボットサービス
- **db**: ヘルスチェック付きPostgreSQLデータベース
- **redis**: Redisキャッシュ/セッションストア
- **db-migrator**: Alembicマイグレーションランナー
- **adminer**: データベース管理インターフェース（開発のみ）
- **db-dumper**: データベースバックアップユーティリティ

環境変数が`INCLUDE_DB`と`INCLUDE_REDIS`フラグによってどのサービスが含まれるかを制御します。

## 開発ワークフロー

1. `make envs:setup`でテンプレートから環境ファイルを作成
2. 各環境ファイルでデータベースとDiscordボットトークンを設定
3. `make dev:setup`で依存関係をインストール
4. `make up INCLUDE_DB=true`でデータベース付きで起動
5. `make db:migrate`でデータベースマイグレーションを適用
6. コミット前に`make lint`と`make format`を使用

## 主要ファイル

- `app/main.py:34-39` - 自動Cogローディングロジック
- `app/core/config.py:78-83` - キャッシュ付き設定ファクトリ
- `app/db/models/base.py:23-31` - タイムスタンプMixin付きベースモデル
- `app/cogs/template.py` - 新しいCog作成用テンプレート
- `app/cogs/admin.py:171-226` - `/status`コマンドとエラーハンドリング
- `app/cogs/cog_manager.py:29-75` - Cog管理コマンド

## 典型的な開発タスク

### 新しいCogを作成
1. `cp app/cogs/template.py app/cogs/new_feature.py`
2. クラス名とsetup関数を更新
3. スラッシュコマンドを`@slash_command`デコレータで追加
4. 開発中は`/reload new_feature`でホットリロード

### データベースモデルを追加
1. `app/db/models/`に新しいモデルファイルを作成
2. `app/db/schemas/`に対応するPydanticスキーマを作成
3. `app/db/crud/`にCRUD操作を作成
4. `make db:revision:create NAME="add_model"`でマイグレーションを作成
5. `make db:migrate`で適用

### 環境設定を追加
1. `app/core/config.py`の`Settings`クラスに新しいフィールドを追加
2. 必要に応じて対応する`.env`ファイルを更新
3. Cogで`self.settings = get_settings()`を使用してアクセス

## テスト

プロジェクトにはセキュリティスキャンが含まれていますが、明示的なテストフレームワークは設定されていません。テストを追加する場合は、プロジェクト構造を確認し、`pyproject.toml`の`dev`グループに適切なテスト依存関係を追加してください。