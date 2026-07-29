from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    PROJECT_NAME: str = "Sistema Jurídico"
    ENVIRONMENT: str = "development"

    # Banco de dados
    DATABASE_URL: str = "postgresql+asyncpg://juridico:juridico@postgres:5432/juridico"

    # Redis / Celery
    REDIS_URL: str = "redis://redis:6379/0"

    # Segurança
    SECRET_KEY: str = "troque-esta-chave-em-producao"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Integrações de tribunais
    DATAJUD_API_KEY: str = ""
    ESCAVADOR_API_KEY: str = ""
    BRASILAPI_FERIADOS_URL: str = "https://brasilapi.com.br/api/feriados/v1"

    # DJEN / Comunica PJe (publicações) — OABs monitoradas no formato "123456/RJ,654321/SP"
    DJEN_BASE_URL: str = "https://comunicaapi.pje.jus.br/api/v1"
    DJEN_OABS: str = ""

    # E-mail
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""
    SENDGRID_API_KEY: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
