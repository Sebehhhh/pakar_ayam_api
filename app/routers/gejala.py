from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.models import Gejala  # Menggunakan model Gejala yang telah diperbarui
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

class GejalaRequest(BaseModel):
    nama: str

@router.get("/gejala")
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    return db.query(Gejala).all()

@router.post("/gejala/store")
async def create_gejala(
    user: user_dependency, gejala_request: GejalaRequest, db: db_dependency
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    # Cek apakah gejala yang baru dimasukkan sudah ada
    existing_gejala = db.query(Gejala).filter(Gejala.nama == gejala_request.nama).first()
    if existing_gejala:
        # Gejala sudah ada, kembalikan respons yang sesuai
        raise HTTPException(status_code=400, detail="Gejala sudah tersedia")

    # Gejala belum ada, lanjutkan dengan proses penyimpanan
    gejala_model = Gejala(**gejala_request.dict())
    db.add(gejala_model)
    db.commit()

    return successful_response(201)


@router.put("/gejala/update/{gejala_id}")
async def update_gejala(
    user: user_dependency, gejala_id: int, gejala: GejalaRequest, db: db_dependency
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    gejala_model = (
        db.query(Gejala)
        .filter(Gejala.id == gejala_id)
        .first()
    )

    if gejala_model is None:
        raise HTTPException(status_code=404, detail="Gejala not found")

    # Cek apakah gejala yang baru dimasukkan sudah ada kecuali jika itu adalah gejala yang sedang diupdate
    existing_gejala = db.query(Gejala).filter(Gejala.nama == gejala.nama, Gejala.id != gejala_id).first()
    if existing_gejala:
        # Gejala sudah ada, kembalikan respons yang sesuai
        raise HTTPException(status_code=400, detail="Gejala sudah tersedia")

    # Update atribut gejala
    gejala_model.nama = gejala.nama

    db.add(gejala_model)
    db.commit()

    return successful_response(200)

@router.delete("/gejala/delete/{gejala_id}")
async def delete_gejala(user: user_dependency, gejala_id: int, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    gejala_model = (
        db.query(Gejala)
        .filter(Gejala.id == gejala_id)
        .first()
    )

    if gejala_model is None:
        raise http_exception()

    db.query(Gejala).filter(Gejala.id == gejala_id).delete()
    db.commit()

    return successful_response(200)

def successful_response(status_code: int):
    return {"status": status_code, "transaction": "Successful"}

def http_exception():
    return HTTPException(status_code=404, detail="Gejala not found")
