from functools import lru_cache
import os
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, "..", ".env")


class Settings(BaseSettings):
    db_user: str
    db_password: str
    db_host: str = "127.0.0.1"
    db_port: int = 3306
    db_name: str
    db_engine_string: str = "mysql+pymysql"
    type_school: str
    api_prefix: str = "/api"
    origins_cors: str = ""
    host_ip: str = "127.0.0.1"

    secret_key: str
    debug: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def origins(self) -> List[str]:
        if not self.origins_cors:
            return ["*"]
        return [origin.strip() for origin in self.origins_cors.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()
