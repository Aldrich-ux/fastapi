from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: Optional[str] = None
    database_username: Optional[str] = None
    database_password: Optional[str] = None
    database_hostname: Optional[str] = None
    database_port: Optional[str] = None
    database_name: Optional[str] = None
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

settings = Settings()
