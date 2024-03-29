from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.models import BasisPengetahuan, Gejala, Penyakit
from app.database import SessionLocal
from .auth import get_current_user
from fastapi import Response

router = APIRouter()

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class BasisPengetahuanRequest(BaseModel):
    penyakit_id: int
    gejala_id: int
    mb: float
    md: float

from fastapi import Response

@router.get("/basis_pengetahuan")
async def read_all(user: user_dependency, db: db_dependency, response: Response):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    basis_pengetahuan_data = db.query(BasisPengetahuan).all()

    # Membuat respons berisi data basis pengetahuan dengan gejala dan penyakit sesuai id
    response_data = []
    for basis_pengetahuan in basis_pengetahuan_data:
        gejala = db.query(Gejala).filter(Gejala.id == basis_pengetahuan.gejala_id).first()
        penyakit = db.query(Penyakit).filter(Penyakit.id == basis_pengetahuan.penyakit_id).first()

        if gejala and penyakit:
            response_data.append({
                "id": basis_pengetahuan.id,
                "penyakit": {
                    "id": penyakit.id,
                    "nama": penyakit.nama,
                    # tambahkan atribut lain yang dibutuhkan
                },
                "gejala": {
                    "id": gejala.id,
                    "nama": gejala.nama,
                    # tambahkan atribut lain yang dibutuhkan
                },
                "mb": basis_pengetahuan.mb,
                "md": basis_pengetahuan.md,
            })

    return response_data

@router.post("/basis_pengetahuan/store")
async def create_basis_pengetahuan(
    user: user_dependency, basis_pengetahuan_request: BasisPengetahuanRequest, db: db_dependency
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    # Memeriksa apakah pasangan gejala dan penyakit sudah ada
    existing_basis_pengetahuan = db.query(BasisPengetahuan).filter(
        BasisPengetahuan.penyakit_id == basis_pengetahuan_request.penyakit_id,
        BasisPengetahuan.gejala_id == basis_pengetahuan_request.gejala_id
    ).first()

    if existing_basis_pengetahuan:
        raise HTTPException(status_code=400, detail="Basis Pengetahuan with the same penyakit_id and gejala_id already exists")

    basis_pengetahuan_model = BasisPengetahuan(**basis_pengetahuan_request.dict())

    db.add(basis_pengetahuan_model)
    db.commit()

    return successful_response(201)

@router.put("/basis_pengetahuan/update/{basis_pengetahuan_id}")
async def update_basis_pengetahuan(
    user: user_dependency, basis_pengetahuan_id: int, basis_pengetahuan: BasisPengetahuanRequest, db: db_dependency
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    basis_pengetahuan_model = (
        db.query(BasisPengetahuan)
        .filter(BasisPengetahuan.id == basis_pengetahuan_id)
        .first()
    )

    if basis_pengetahuan_model is None:
        raise HTTPException(status_code=404, detail="Basis Pengetahuan not found")

    # Memeriksa apakah pasangan gejala dan penyakit sudah ada
    existing_basis_pengetahuan = db.query(BasisPengetahuan).filter(
        BasisPengetahuan.penyakit_id == basis_pengetahuan.penyakit_id,
        BasisPengetahuan.gejala_id == basis_pengetahuan.gejala_id
    ).filter(
        BasisPengetahuan.id != basis_pengetahuan_id  # Untuk memungkinkan pembaruan data tanpa menghasilkan kesalahan validasi
    ).first()

    if existing_basis_pengetahuan:
        raise HTTPException(status_code=400, detail="Basis Pengetahuan with the same penyakit_id and gejala_id already exists")

    basis_pengetahuan_model.penyakit_id = basis_pengetahuan.penyakit_id
    basis_pengetahuan_model.gejala_id = basis_pengetahuan.gejala_id
    basis_pengetahuan_model.mb = basis_pengetahuan.mb
    basis_pengetahuan_model.md = basis_pengetahuan.md

    db.add(basis_pengetahuan_model)
    db.commit()

    return successful_response(200)
@router.delete("/basis_pengetahuan/delete/{basis_pengetahuan_id}")
async def delete_basis_pengetahuan(user: user_dependency, basis_pengetahuan_id: int, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    basis_pengetahuan_model = (
        db.query(BasisPengetahuan)
        .filter(BasisPengetahuan.id == basis_pengetahuan_id)
        .first()
    )

    if basis_pengetahuan_model is None:
        raise http_exception()

    db.query(BasisPengetahuan).filter(BasisPengetahuan.id == basis_pengetahuan_id).delete()
    db.commit()

    return successful_response(200)

def successful_response(status_code: int):
    return {"status": status_code, "transaction": "Successful"}

def http_exception():
    return HTTPException(status_code=404, detail="Basis Pengetahuan not found")
