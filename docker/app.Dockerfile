FROM python:3.12.7-slim

WORKDIR /app

RUN apt update && \
    apt upgrade -y && \
    apt install -y build-essential git nano curl \
    tzdata libpq-dev gcc make && \
    pip install --upgrade pip poetry

# install requirements
COPY ./app/poetry.lock ./app/pyproject.toml ./app/Makefile /app/
RUN poetry config virtualenvs.create false
RUN make poetry:install

# add poetry files for symlinks
COPY ./pyproject.toml ./poetry.lock /

CMD ["python", "main.py"]