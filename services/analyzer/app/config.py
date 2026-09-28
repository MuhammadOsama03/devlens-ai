from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    github_token: str | None = None
    api_key_hash: str | None = None
    github_api_url: str = "https://api.github.com"
    request_timeout_seconds: float = Field(default=10.0, gt=0)
    cache_ttl_seconds: float = Field(default=300.0, gt=0)
    cache_max_entries: int = Field(default=256, gt=0)
    database_path: str = "devlens.db"
    rate_limit_requests: int = Field(default=60, gt=0)
    rate_limit_window_seconds: float = Field(default=60.0, gt=0)
    cors_origins: str = "http://localhost:3000"
    max_context_file_bytes: int = Field(default=100_000, gt=0, le=1_000_000)

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
