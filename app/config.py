# app/config.py
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "IntelliDocs"
    SECRET_KEY: str = "super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # Neon PostgreSQL URL
    DATABASE_URL: str = "sqlite:///./intellidocs.db"
        # CROS 
    CORS_ORIGINS: list[str] = [
            "https://intelli-docs-mu.vercel.app",
            "http://localhost:3000",
            "http://localhost:8000",
        ]

    # Neon Object Storage Config
    NEON_STORAGE_ENDPOINT: str = ""
    NEON_STORAGE_REGION: str = "us-east-2"
    NEON_STORAGE_ACCESS_KEY_ID: str = ""
    NEON_STORAGE_SECRET_ACCESS_KEY: str = ""
    NEON_STORAGE_BUCKET_NAME: str = "intellidocs"

    # Paths & ChromaDB
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    CHROMA_PERSIST_DIR: Path = BASE_DIR / "chroma_db"

    # Groq & RAG
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "openai/gpt-oss-20b"
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"

    # Email OTP
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
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url

settings = Settings()
settings.CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)