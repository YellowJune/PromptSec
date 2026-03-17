"""Settings management using Pydantic BaseSettings for environment variable loading."""

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "PromptSec"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "Advanced LLM Security Analysis & Red Teaming Platform"

    DATABASE_URL: str = "sqlite:///./promptsec.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    OPENAI_API_KEY: Optional[str] = None
    HUGGINGFACE_MODEL_PATH: str = "distilgpt2"
    HUGGINGFACE_TOKEN: Optional[str] = None

    DETECTOR_RULE_WEIGHT: float = 0.3
    DETECTOR_HEURISTIC_WEIGHT: float = 0.3
    DETECTOR_LLM_WEIGHT: float = 0.4
    DETECTOR_RISK_THRESHOLD: float = 0.6

    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
