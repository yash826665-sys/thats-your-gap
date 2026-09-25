"""
Centralized configuration, loaded from environment variables.

Nothing secret ever ships to the frontend. The frontend only ever calls
our own backend endpoints; the backend is the only thing that talks to
the LLM provider.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- LLM provider ---
    llm_provider: str = "ollama"
    anthropic_api_key: str = ""
    llm_model: str = "qwen3.5:2b"
    llm_max_output_tokens: int = 4000
    llm_timeout_seconds: int = 60
    llm_max_retries: int = 2

    # --- Upload limits ---
    max_upload_size_mb: int = 10
    allowed_upload_mime_types: str = "application/pdf"

    # --- Text size guards (protect LLM context / cost) ---
    max_extracted_chars_per_doc: int = 20000
    max_job_description_chars: int = 8000

    # --- App ---
    environment: str = "development"
    cors_allowed_origins: str = "http://localhost:3000"
    log_level: str = "INFO"

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_allowed_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
