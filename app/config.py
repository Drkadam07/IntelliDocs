import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "IntelliDocs"
    SECRET_KEY: str = "super-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    DATABASE_URL: str = "sqlite:///./intellidocs.db"

    #CROS 
    CORS_ORIGINS: list[str] = [
            "https://intelli-docs-mu.vercel.app",
            "http://localhost:3000",
            "http://localhost:8000",
        ]
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    CHROMA_PERSIST_DIR: Path = BASE_DIR / "chroma_db"

    # Groq & RAG
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_EMAIL: str = "noreply@intellidocs.local"
    EMAILS_FROM_NAME: str = "IntelliDocs"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
