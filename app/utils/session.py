from typing import Optional

from core import get_settings
from utils.redis import RedisCrud
from utils.schemas import SessionSchema

settings = get_settings()


class SessionCrud:
    """
    セッション管理クラス
    """

    def __init__(self):
        """
        初期化
        """
        self.crud = RedisCrud(db=0)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.crud.__exit__(exc_type, exc_value, traceback)

    def get(self, key: str) -> Optional[SessionSchema]:
        """
        セッションデータ取得
        """
        raw = self.crud.get(key)
        if raw is None:
            return None
        return SessionSchema.model_validate(raw)

    def set(self, key: str, value: SessionSchema, expire: int | None = None) -> bool:
        """
        セッションデータ設定
        """
        return self.crud.set(key, value.model_dump(), expire=expire)

    def delete(self, key: str) -> int:
        """
        セッションデータ削除
        """
        return self.crud.delete(key)
