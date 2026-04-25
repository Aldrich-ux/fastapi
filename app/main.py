from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
import psycopg
from psycopg.rows import dict_row
import time


app = FastAPI()


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
def create_post(post: Post):
    # Note: do not use f-string to avoid SQL injection attack
    new_post = cursor.execute(
        "INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *",
        (post.title, post.content, post.published)).fetchone() 
    # Note: cursor.execute() only staged changes,
    # you need to commit() to save changes to database (similar to `git`)
    conn.commit() 
    
    return {"post": new_post}

 
@app.get("/posts")
def get_posts():
    posts = cursor.execute("SELECT * FROM posts").fetchall()
    return {"data": posts}


# {id} called path_parameter
@app.get("/posts/{id}")
def get_post(id: int):
    cursor.execute("SELECT * FROM posts WHERE id = %s", (id,))
    post = cursor.fetchone()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found"
        )
    
    return {"post_detail": post}


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute(
        "UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *",
        (post.title, post.content, post.published, id))
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found"
        )
    
    return {"data": updated_post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute("DELETE FROM posts WHERE id = %s RETURNING *", (id,))
    deleted_post = cursor.fetchone()
    conn.commit()

    if deleted_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found"
        )
    
    # 204 expects no content be returned
    return Response(status_code=status.HTTP_204_NO_CONTENT)
