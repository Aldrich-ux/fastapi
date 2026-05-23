from fastapi import FastAPI
from . import models
from .database import engine
from .routers import post, user, auth, vote


# ------------------ Note: CRUD Operations ------------------
# Basic operation of application
# CRUD - Create, Read, Update, Delete
# Create: Post:      @app.post("/posts")
# Read:   Get:       @app.get("/posts/{id}") or @app.get("/posts")
# Update: Put/Patch: @app.put("/posts/{id}")
# Delete: Delete:    @app.delete("/posts/{id}")
# -----------------------------------------------------------


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

# path_operation = url("/") + http_method("get") + function("root")
@app.get("/")
def root():
    return {"message": "Welcome to my first API!"}
