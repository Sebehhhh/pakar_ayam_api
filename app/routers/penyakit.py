from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

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

    # Cek apakah nama penyakit sudah tersedia
    existing_penyakit = db.query(Penyakit).filter(Penyakit.nama == penyakit_request.nama).first()
    if existing_penyakit:
        # Nama penyakit sudah ada, kembalikan respons yang sesuai
        raise HTTPException(status_code=400, detail="Nama penyakit sudah tersedia")

    # Nama penyakit belum ada, lanjutkan dengan proses penyimpanan
    penyakit_model = Penyakit(**penyakit_request.dict())
    db.add(penyakit_model)
    db.commit()

    return successful_response(201)


@router.get("/penyakit/{penyakit_id}")
async def get_penyakit_by_id(user: user_dependency, penyakit_id: int, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    penyakit_model = (
        db.query(Penyakit)
        .filter(Penyakit.id == penyakit_id)
        .first()
    )

    if penyakit_model is None:
        raise HTTPException(status_code=404, detail="Penyakit not found")

    return penyakit_model


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

    # Cek apakah nama penyakit yang baru dimasukkan sudah ada kecuali jika itu adalah nama penyakit yang sedang diupdate
    existing_penyakit = db.query(Penyakit).filter(Penyakit.nama == penyakit.nama, Penyakit.id != penyakit_id).first()
    if existing_penyakit:
        # Nama penyakit sudah ada, kembalikan respons yang sesuai
        raise HTTPException(status_code=400, detail="Nama penyakit sudah tersedia")

    # Update atribut penyakit
    penyakit_model.nama = penyakit.nama
    penyakit_model.detail = penyakit.detail
    penyakit_model.saran = penyakit.saran
    penyakit_model.gambar = penyakit.gambar

    db.add(penyakit_model)
    db.commit()

    return successful_response(201)

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
        raise HTTPException(status_code=404, detail="Penyakit not found")

    gambar = penyakit_model.gambar  # Menyimpan nama penyakit yang dihapus
    db.query(Penyakit).filter(Penyakit.id == penyakit_id).delete()
    db.commit()

    return {"status_code": 200, "message": "Penyakit deleted successfully", "gambar": gambar}


def successful_response(status_code: int):
    return {"status": status_code, "transaction": "Successful"}

def http_exception():
    return HTTPException(status_code=404, detail="Penyakit not found")
