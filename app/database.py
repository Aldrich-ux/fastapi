from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .config import settings


def get_database_url() -> str:
    if settings.database_url:
        return settings.database_url

    if not all(
        [
            settings.database_username,
            settings.database_password,
            settings.database_hostname,
            settings.database_port,
            settings.database_name,
        ]
    ):
        raise ValueError(
            "Database configuration is incomplete. Set DATABASE_URL or the individual database_* variables."
        )

    return (
        f"postgresql+psycopg2://{settings.database_username}:{settings.database_password}"
        f"@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"
    )


SQLALCHEMY_DATABASE_URL = get_database_url()

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
