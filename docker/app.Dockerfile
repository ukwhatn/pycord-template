FROM python:3.12.9-slim

# timezone設定
ENV TZ=Asia/Tokyo
ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT='/usr/local/'
ENV UV_SYSTEM_PYTHON=1

# システム依存パッケージインストール
RUN apt update && \
    apt upgrade -y && \
    apt install -y build-essential git nano curl \
    tzdata libpq-dev gcc make

# uvのインストール
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 作業ディレクトリ設定
WORKDIR /usr/src

# 依存関係ファイルをコピー
COPY pyproject.toml uv.lock /usr/src/

# 依存関係インストール
RUN uv sync --group discord --group db --frozen --no-dev --no-cache

# 非rootユーザーを作成
RUN adduser --disabled-password --gecos "" nonroot
RUN chown -R nonroot:nonroot /usr/src

# 非rootユーザーに切り替え
USER nonroot

# アプリケーションディレクトリに移動
WORKDIR /usr/src/app

CMD ["python", "main.py"]