from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "BestOfUs"
    debug: bool = False
    api_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./bestofus.db"

    # Signs login tokens. Required, no default: must be a long random string in .env.
    # Generate one with: python3 -c "import secrets; print(secrets.token_urlsafe(32))"
    secret_key: str
    access_token_expire_minutes: int = 60 * 24 * 7  # one week

    # Where uploaded photos are stored on disk (not in git).
    media_dir: str = "media"

    # Push notifications go through Expo's free push service to Apple and Google.
    expo_push_url: str = "https://exp.host/--/api/v2/push/send"
    expo_access_token: str | None = None  # optional, from expo.dev if "enhanced security" is on


settings = Settings()
