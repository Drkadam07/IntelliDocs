# app/config.py
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "IntelliDocs"
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # CROS 
    CORS_ORIGINS: list[str] = [
            "https://intelli-docs-mu.vercel.app",
            "http://localhost:3000",
            "http://localhost:8000",
        ]
    # PostgreSQL Database URL (Neon or Supabase)
    DATABASE_URL: str = ""

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

    @property
    def normalized_database_url(self) -> str:
        url = self.DATABASE_URL.strip()
        # Fix SQLAlchemy dialect prefix if copied as postgres://
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url

settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)