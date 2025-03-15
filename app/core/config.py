from functools import lru_cache
from typing import Literal, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    アプリケーション設定
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # 環境設定
    ENV_MODE: Literal["development", "production", "test"] = "development"

    BOT_TOKEN: str = ""

    # セキュリティヘッダー設定
    SECURITY_HEADERS: bool = True
    CSP_POLICY: str = (
        "default-src 'self'; img-src 'self' data:; script-src 'self'; style-src 'self'"
    )

    # データベース設定
    POSTGRES_USER: str = "user"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "main"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: str = "5432"

    @property
    def DATABASE_URI(self) -> str:
        """
        データベース接続URLを取得
        """
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Redis設定
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    # Sentry設定
    SENTRY_DSN: Optional[str] = None
    SENTRY_TRACES_SAMPLE_RATE: float = 1.0

    @classmethod
    @field_validator("SENTRY_DSN")
    def sentry_dsn_can_be_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return None
        return v

    @property
    def is_development(self) -> bool:
        """開発環境かどうか"""
        return self.ENV_MODE == "development"

    @property
    def is_production(self) -> bool:
        """本番環境かどうか"""
        return self.ENV_MODE == "production"

    @property
    def is_test(self) -> bool:
        """テスト環境かどうか"""
        return self.ENV_MODE == "test"


@lru_cache
def get_settings() -> Settings:
    """
    アプリケーション設定を取得（キャッシュ）
    """
    return Settings()
