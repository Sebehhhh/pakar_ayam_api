from decimal import Decimal
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.models import BasisPengetahuan, Penyakit
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

class DiagnosisRequest(BaseModel):
    kondisi: list
    threshold: float = Field(..., description="Threshold for diagnosis")

class DiagnosisResponse(BaseModel):
    penyakit: str
    keyakinan: float
@router.post("/diagnosis")
async def diagnosis(
    user: user_dependency, diagnosis_request: DiagnosisRequest, db: db_dependency
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    
    kondisi = diagnosis_request.kondisi
    threshold = diagnosis_request.threshold

    penyakit_cf = {}  # dictionary untuk menyimpan CF penyakit

    # Hitung CF untuk setiap penyakit berdasarkan gejala
    for penyakit in db.query(Penyakit).all():
        cf_total_temp = Decimal(0)
        cf_total_temp = cf_total_temp.quantize(Decimal('0.00'))
        for gejala in kondisi:
            gejala_id = gejala['gejala_id']
            bobot = Decimal(gejala['bobot']).quantize(Decimal('0.00')) # Konversi bobot menjadi Decimal
            basis_pengetahuan = db.query(BasisPengetahuan).filter(
                BasisPengetahuan.gejala_id == gejala_id,
                BasisPengetahuan.penyakit_id == penyakit.id
            ).first()
            if basis_pengetahuan:
                # Hitung CF
                cf = (basis_pengetahuan.mb - basis_pengetahuan.md) * bobot
                
                # Perhitungan fungsi korespondensi
                if (cf >= 0) and (cf * cf_total_temp >= 0):
                    cf_total_temp += cf * (1 - cf_total_temp)
                elif (cf * cf_total_temp < 0):
                    cf_total_temp = (cf_total_temp + cf) / (1 - min(abs(cf_total_temp), abs(cf)))
                elif (cf < 0) and (cf * cf_total_temp >= 0):
                    cf_total_temp += cf * (1 + cf_total_temp)

        if cf_total_temp > threshold:
            # Membatasi hanya dua angka di belakang koma
            cf_total_temp = cf_total_temp.quantize(Decimal('0.00'))
            penyakit_cf[penyakit.nama] = cf_total_temp
    
    # Urutkan penyakit berdasarkan keyakinan (CF) dari yang tertinggi
    sorted_penyakit_cf = dict(sorted(penyakit_cf.items(), key=lambda item: item[1], reverse=True))

    # Buat respons diagnosis
    diagnosis_response = []
    for penyakit, keyakinan in sorted_penyakit_cf.items():
        diagnosis_response.append(DiagnosisResponse(penyakit=penyakit, keyakinan=float(keyakinan)))

    return diagnosis_response
