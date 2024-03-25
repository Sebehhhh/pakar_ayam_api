from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.models import BasisPengetahuan
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

class BasisPengetahuanRequest(BaseModel):
    penyakit_id: int
    gejala_id: int
    mb: float
    md: float

@router.get("/basis_pengetahuan")
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    return db.query(BasisPengetahuan).all()

@router.post("/basis_pengetahuan/store")
async def create_basis_pengetahuan(
    user: user_dependency, basis_pengetahuan_request: BasisPengetahuanRequest, db: db_dependency
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

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
        raise http_exception()

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