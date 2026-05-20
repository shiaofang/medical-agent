from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ollama_api_key: str = ""
    ollama_host: str = "https://ollama.com"
    ollama_model: str = "gpt-oss:120b"

    app_title: str = "Medical Assistant API"
    cors_origins: str = "*"


settings = Settings()
