FROM python:3.12.9-slim

# timezone設定
ENV TZ=Asia/Tokyo

WORKDIR /app

RUN apt update && \
    apt upgrade -y && \
    apt install -y build-essential git nano curl \
    tzdata libpq-dev gcc make && \
    pip install --upgrade pip poetry

# Poetryの設定
RUN poetry config virtualenvs.create false

# 依存関係ファイルをコピー
COPY pyproject.toml poetry.lock ./

# 依存関係インストール
RUN poetry install --with discord,db

# 非rootユーザーを作成
RUN adduser --disabled-password --gecos "" nonroot
RUN chown -R nonroot:nonroot /app

# 非rootユーザーに切り替え
USER nonroot

CMD ["python", "main.py"]