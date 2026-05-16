from typing import List
from fastapi import Depends, FastAPI, Response, status, HTTPException
import psycopg
from psycopg.rows import dict_row
import time
from sqlalchemy.orm import Session
from . import models, schemas, utils
from .database import engine, get_db
from .routers import post, user


# ------------------ Note: CRUD Operations ------------------
# Basic operation of application
# CRUD - Create, Read, Update, Delete
# Create: Post:      @app.post("/posts")
# Read:   Get:       @app.get("/posts/{id}") or @app.get("/posts")
# Update: Put/Patch: @app.put("/posts/{id}")
# Delete: Delete:    @app.delete("/posts/{id}")
# -----------------------------------------------------------


app = FastAPI()


models.Base.metadata.create_all(bind=engine)


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


app.include_router(post.router)
app.include_router(user.router)

# path_operation = url("/") + http_method("get") + function("root")
@app.get("/")
def root():
    return {"message": "Welcome to my first API!"}
