from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.models import Penyakit, Post  # Menambahkan model Post
from app.database import SessionLocal
from .auth import get_current_user

router = APIRouter()

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class PostRequest(BaseModel):
    nama: str
    detail: str
    saran: Optional[str] = None
    gambar: Optional[str] = None

@router.get("/post")
async def read_all_post(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    return db.query(Post).all()

@router.post("/post/store")
async def create_post(
    user: user_dependency, post_request: PostRequest, db: db_dependency
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    post_model = Post(**post_request.dict())

    db.add(post_model)
    db.commit()

    return successful_response(201)

@router.put("/post/update/{post_id}")
async def update_post(
    user: user_dependency, post_id: int, post: PostRequest, db: db_dependency
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    post_model = (
        db.query(Post)
        .filter(Post.id == post_id)
        .first()
    )

    if post_model is None:
        raise http_exception()

    post_model.nama = post.nama
    post_model.detail = post.detail
    post_model.saran = post.saran
    post_model.gambar = post.gambar

    db.add(post_model)
    db.commit()

    return successful_response(200)

@router.delete("/post/delete/{post_id}")
async def delete_post(user: user_dependency, post_id: int, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    post_model = (
        db.query(Post)
        .filter(Post.id == post_id)
        .first()
    )

    if post_model is None:
        raise http_exception()

    db.query(Post).filter(Post.id == post_id).delete()
    db.commit()

    return successful_response(200)

def successful_response(status_code: int):
    return {"status": status_code, "transaction": "Successful"}

def http_exception():
    return HTTPException(status_code=404, detail="Post not found")
