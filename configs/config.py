from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_SOURCE_URLS = [
    "https://lilianweng.github.io/posts/2023-06-23-agent/",
    "https://lilianweng.github.io/posts/2024-04-12-diffusion-video/",
]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ollama_base_url: str = "http://localhost:11434"
    ollama_chat_model: str = "llama3.2:3b"
    ollama_embed_model: str = "bge-m3:latest"
    ollama_temperature: float = 0.2
    user_agent: str = "query-planning-decomposition/0.1"
    chunk_size: int = 500
    chunk_overlap: int = 50
    source_urls: list[str] = Field(default_factory=lambda: list(DEFAULT_SOURCE_URLS))


@lru_cache
def get_settings() -> Settings:
    return Settings()
