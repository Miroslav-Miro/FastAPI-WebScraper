"""
Database configuration and session management for the Web Scraper API.

- Loads database connection details from environment variables.
- Creates SQLAlchemy engine and session factory.
- Provides a session generator dependency for FastAPI routes.

Uses PostgreSQL with psycopg2 driver.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()


def get_db():
    """
    Provide a database session for a request and ensure it is closed after use.

    This function is a generator yielding a SQLAlchemy SessionLocal instance.
    It is designed to be used as a FastAPI dependency to handle DB sessions.

    Yields:
        Session: SQLAlchemy database session instance.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
