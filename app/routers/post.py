from fastapi import Depends, Response, status, HTTPException, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from .. import models, schemas, oauth2
from ..database import get_db


router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, 
                db: Session = Depends(get_db),
                current_user: models.User = Depends(oauth2.get_current_user)):
    # Note: do not use f-string to avoid SQL injection attack
    # new_post = cursor.execute(
    #     "INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *",
    #     (post.title, post.content, post.published)).fetchone() 
    # Note: cursor.execute() only staged changes,
    # you need to commit() to save changes to database (similar to `git`)
    # conn.commit() 
    new_post = models.Post(**post.model_dump(), owner_id=current_user.id) # SQLAlchemy model
    db.add(new_post) # stage changes
    db.commit() # commit to database
    db.refresh(new_post) # refresh instance with new data from database

    return new_post

 
# @router.get("/", response_model=List[schemas.Post])
@router.get("/", response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db),
              current_user: models.User = Depends(oauth2.get_current_user),
              limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    # posts = cursor.execute("SELECT * FROM posts").fetchall()
    # posts = (db.query(models.Post)
    #          .filter(models.Post.title.contains(search))
    #          .limit(limit).offset(skip).all())
    
    # posts: [(models.Post object, int(vote) object), ...]
    posts = (db.query(models.Post, func.count(models.Vote.post_id).label('vote'))
               .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
               .group_by(models.Post.id)
               .filter(models.Post.title.contains(search))
               .limit(limit).offset(skip)
               .all())
    
    return [
        {"post": post, "vote": vote}
        for post, vote in posts
    ]


# {id} called path_parameter
@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db),
             current_user: models.User = Depends(oauth2.get_current_user)):
    # cursor.execute("SELECT * FROM posts WHERE id = %s", (id,))
    # post = cursor.fetchone()
    # post = db.query(models.Post).filter(models.Post.id == id).first()

    post = (db.query(models.Post, func.count(models.Vote.post_id).label('vote'))
               .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
               .group_by(models.Post.id)
               .filter(models.Post.id == id).first())
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found"
        )
    
    return {"post": post.Post, "vote": post.vote}


@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, post: schemas.PostCreate, 
                db: Session = Depends(get_db),
                current_user: models.User = Depends(oauth2.get_current_user)):
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
    
    if updated_post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action"
        )
    
    # Note: pydantic model (post) != SQLAlchemy model (updated_post)
    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()
    
    return post_query.first()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db),
                current_user: models.User = Depends(oauth2.get_current_user)):
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
    
    if deleted_post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action"
        )
    
    post_query.delete(synchronize_session=False)
    db.commit()
    
    # 204 expects no content be returned
    return Response(status_code=status.HTTP_204_NO_CONTENT)
