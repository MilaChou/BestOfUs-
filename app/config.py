from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "BestOfUs"
    debug: bool = False
    api_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./bestofus.db"


settings = Settings()
