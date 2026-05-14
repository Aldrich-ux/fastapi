from fastapi import Depends, FastAPI, Response, status, HTTPException
from pydantic import BaseModel
import psycopg
from psycopg.rows import dict_row
import time
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db


models.Base.metadata.create_all(bind=engine)


app = FastAPI()


# pydantic/schema model define the structure of a request & response
class Post(BaseModel):
    title: str
    content: str
    published: bool = True


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


# ------------------ Note: CRUD Operations ------------------
# Basic operation of application
# CRUD - Create, Read, Update, Delete
# Create: Post:      @app.post("/posts")
# Read:   Get:       @app.get("/posts/{id}") or @app.get("/posts")
# Update: Put/Patch: @app.put("/posts/{id}")
# Delete: Delete:    @app.delete("/posts/{id}")
# -----------------------------------------------------------


# path_operation = url("/") + http_method("get") + function("root")
@app.get("/")
def root():
    return {"message": "Welcome to my first API!"}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post, db: Session = Depends(get_db)):
    # Note: do not use f-string to avoid SQL injection attack
    # new_post = cursor.execute(
    #     "INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *",
    #     (post.title, post.content, post.published)).fetchone() 
    # Note: cursor.execute() only staged changes,
    # you need to commit() to save changes to database (similar to `git`)
    # conn.commit() 
    new_post = models.Post(**post.model_dump())
    db.add(new_post) # stage changes
    db.commit() # commit to database
    db.refresh(new_post) # refresh instance with new data from database

    return {"post": new_post}

 
@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    # posts = cursor.execute("SELECT * FROM posts").fetchall()
    posts = db.query(models.Post).all()
    return {"data": posts}


@app.get("/sqlalchemy")
def test_post(db: Session = Depends(get_db)):
    # send actually raw SQL command,
    # but write code with abstracted way.
    posts = db.query(models.Post).all()
    return {"data": posts}


# {id} called path_parameter
@app.get("/posts/{id}")
def get_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("SELECT * FROM posts WHERE id = %s", (id,))
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found"
        )
    
    return {"post_detail": post}


@app.put("/posts/{id}")
def update_post(id: int, post: Post, db: Session = Depends(get_db)):
    # cursor.execute(
    #     "UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *",
    #     (post.title, post.content, post.published, id))
    # updated_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    updated_post = post_query.first()

    if updated_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found"
        )
    
    # Note: pydantic model (post) != SQLAlchemy model (updated_post)
    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()
    
    return {"data": post_query.first()}
    

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("DELETE FROM posts WHERE id = %s RETURNING *", (id,))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    deleted_post = post_query.first()

    if deleted_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found"
        ) 
    
    post_query.delete(synchronize_session=False)
    db.commit()
    
    # 204 expects no content be returned
    return Response(status_code=status.HTTP_204_NO_CONTENT)
