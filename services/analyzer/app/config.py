from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    github_token: str | None = None
    github_api_url: str = "https://api.github.com"
    request_timeout_seconds: float = Field(default=10.0, gt=0)
    cache_ttl_seconds: float = Field(default=300.0, gt=0)
    cache_max_entries: int = Field(default=256, gt=0)
    database_path: str = "devlens.db"
    rate_limit_requests: int = Field(default=60, gt=0)
    rate_limit_window_seconds: float = Field(default=60.0, gt=0)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
