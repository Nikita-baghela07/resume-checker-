from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

def _parse_origins(raw: str) -> List[str]:
    """Parse a comma-separated origins string into a list."""
    return [o.strip() for o in raw.split(",") if o.strip()]

class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "claude-sonnet-4-20250514")
    SBERT_MODEL: str = os.getenv("SBERT_MODEL", "all-MiniLM-L6-v2")
    ALLOWED_ORIGINS: List[str] = _parse_origins(
        os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
    )
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "2000"))
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB

    class Config:
        env_file = ".env"

settings = Settings()
