"""Configurações da aplicação (12-factor: tudo via variáveis de ambiente)."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "Raízes do Nordeste - Backend API"
    app_version: str = "1.0.0"
    debug: bool = False
    database_url: str = "sqlite:///./raizes.db"
    secret_key: str = "raizes_secret_key_troque_em_producao"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 120
    auto_seed: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
