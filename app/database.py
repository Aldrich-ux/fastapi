from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import psycopg
from psycopg.rows import dict_row
import time


# SQLALCHEMY_DATABASE_URL = "postgresql://<username>:<password>@<host>/<database_name>"
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:aldrich1028@localhost/fastapi"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


while True:
    try:
        conn = psycopg.connect(
            conninfo="host=localhost dbname=fastapi user=postgres password=aldrich1028",
            row_factory=dict_row)
        cursor = conn.cursor()
        print("Database connection was successful!")
        break
    except Exception as e:
        print("Database connection failed!")
        print("Error:", e)
        time.sleep(2)