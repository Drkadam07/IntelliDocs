# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

db_url = settings.normalized_database_url

if "sqlite" in db_url:
    # Local fallback for development testing
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False}
    )
else:
    # Production PostgreSQL connection configuration (Neon / Supabase)
    engine = create_engine(
        db_url,
        pool_pre_ping=True,      # Tests connection liveness before executing queries
        pool_recycle=300,        # Recycles connections every 5 minutes to prevent dropped sockets
        pool_size=10,            # Max persistent connections
        max_overflow=20          # Extra connections allowed during peak traffic
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()