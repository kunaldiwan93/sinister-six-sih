import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "NEXUS Investigation Intelligence System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str = Field(
        default="sqlite:///./nexus.db",
        description="PostgreSQL or SQLite database connection URL"
    )
    
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "*"
    ]
    
    # AI LLM Provider Configuration
    LLM_PROVIDER: str = "local"  # local | openai | gemini | anthropic
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    
    # Upload settings
    MAX_UPLOAD_SIZE_MB: int = 25
    ALLOWED_EXTENSIONS: List[str] = [".txt", ".pdf", ".docx", ".csv", ".json"]
    UPLOAD_DIR: str = "./uploads"

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
