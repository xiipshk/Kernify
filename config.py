"""Configuration settings for the Telegram bot."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Telegram Bot
    BOT_TOKEN: str = Field(..., description="Telegram Bot Token from @BotFather")

    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./bot.db",
        description="Database connection URL"
    )

    # AI/LLM
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API Key")
    ANTHROPIC_API_KEY: str = Field(default="", description="Anthropic API Key")
    DEFAULT_AI_PROVIDER: str = Field(default="openai", description="Default AI provider: openai or anthropic")
    AI_MODEL: str = Field(default="gpt-4o-mini", description="AI model to use")

    # Code Execution
    PISTON_API_URL: str = Field(
        default="https://emkc.org/api/v2/piston",
        description="Piston API URL for code execution"
    )
    CODE_EXECUTION_TIMEOUT: int = Field(default=10, description="Code execution timeout in seconds")

    # Bot Settings
    ADMIN_USER_IDS: list[int] = Field(default_factory=list, description="List of admin user IDs")
    MAX_MESSAGE_LENGTH: int = Field(default=4096, description="Max Telegram message length")
    DEFAULT_LANGUAGE: str = Field(default="ru", description="Default bot language")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(default="json", description="Log format: json or console")

    # Paths
    BASE_DIR: Path = Field(default_factory=lambda: Path(__file__).parent)
    DATA_DIR: Path = Field(default_factory=lambda: Path(__file__).parent / "data")
    LOCALES_DIR: Path = Field(default_factory=lambda: Path(__file__).parent / "locales")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()