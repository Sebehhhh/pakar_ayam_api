from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.models import Penyakit  # Menggunakan model Penyakit yang telah diperbarui
from app.database import SessionLocal

router = APIRouter()

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/homepage")
async def read_all(db: db_dependency):
    return db.query(Penyakit).all()
