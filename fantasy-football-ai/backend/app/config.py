"""Configuration settings for the Fantasy Football AI Draft Evaluator."""

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    ANTHROPIC_API_KEY: str | None = None
    SPORTRADAR_API_KEY: str | None = None
    SLEEPER_BASE_URL: str
    MLFLOW_TRACKING_URI: str
    ENVIRONMENT: str = "development"


settings = Settings()
