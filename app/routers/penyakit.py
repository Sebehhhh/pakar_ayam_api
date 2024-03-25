from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.models import Penyakit  # Menggunakan model Penyakit yang telah diperbarui
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

class PenyakitRequest(BaseModel):
    nama: str
    detail: str
    saran: Optional[str] = None
    gambar: Optional[str] = None

@router.get("/penyakit")
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    return db.query(Penyakit).all()

@router.post("/penyakit/store")
async def create_penyakit(
    user: user_dependency, penyakit_request: PenyakitRequest, db: db_dependency
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    penyakit_model = Penyakit(**penyakit_request.dict())

    db.add(penyakit_model)
    db.commit()

    return successful_response(201)

@router.put("/penyakit/update/{penyakit_id}")
async def update_penyakit(
    user: user_dependency, penyakit_id: int, penyakit: PenyakitRequest, db: db_dependency
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    penyakit_model = (
        db.query(Penyakit)
        .filter(Penyakit.id == penyakit_id)
        .first()
    )

    if penyakit_model is None:
        raise http_exception()

    penyakit_model.nama = penyakit.nama
    penyakit_model.detail = penyakit.detail
    penyakit_model.saran = penyakit.saran
    penyakit_model.gambar = penyakit.gambar

    db.add(penyakit_model)
    db.commit()

    return successful_response(200)

@router.delete("/penyakit/delete/{penyakit_id}")
async def delete_penyakit(user: user_dependency, penyakit_id: int, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    penyakit_model = (
        db.query(Penyakit)
        .filter(Penyakit.id == penyakit_id)
        .first()
    )

    if penyakit_model is None:
        raise http_exception()

    db.query(Penyakit).filter(Penyakit.id == penyakit_id).delete()
    db.commit()

    return successful_response(200)

def successful_response(status_code: int):
    return {"status": status_code, "transaction": "Successful"}

def http_exception():
    return HTTPException(status_code=404, detail="Penyakit not found")