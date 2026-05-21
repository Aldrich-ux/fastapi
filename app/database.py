from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import psycopg  # noqa: F401
from psycopg.rows import dict_row  # noqa: F401
import time  # noqa: F401
from .config import settings


# SQLALCHEMY_DATABASE_URL = "postgresql://<username>:<password>@<host>/<database_name>"
SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{settings.database_username}:{settings.database_password}"
    f"@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# while True:
#     try:
#         conn = psycopg.connect(
#             conninfo=(
#                 f"host={settings.database_hostname} "
#                 f"dbname={settings.database_name} "
#                 f"user={settings.database_username} "
#                 f"password={settings.database_password} "
#                 f"port={settings.database_port}"
#             ),
#             row_factory=dict_row)
#         cursor = conn.cursor()
#         print("Database connection was successful!")
#         break
#     except Exception as e:
#         print("Database connection failed!")
#         print("Error:", e)
#         time.sleep(2)
