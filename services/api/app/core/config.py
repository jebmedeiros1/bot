from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    jwt_secret: str
    jwt_expire_minutes: int = 120
    webhook_global_url: str
    evolution_server_url: str
    evolution_apikey: str
    redis_url: str
    app_env: str = "development"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)


settings = Settings()
