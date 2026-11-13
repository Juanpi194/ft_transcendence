from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import Generator

# +psycopg tells to postgre that the version i have installed is the one to use
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg://transcendence_user:transcendence_password@db:5432/transcendence_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
