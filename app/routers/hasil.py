from decimal import Decimal
from typing import Annotated, Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime
from app.models import BasisPengetahuan, Penyakit, Gejala, Hasil  # Tambahkan model Hasil
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
    gejala: List[str]
    kemungkinan: str
    detail: Optional[str]
    saran: Optional[str]
    gambar: Optional[str]
    request_data: DiagnosisRequest  # Menyimpan data permintaan diagnosa
@router.post("/diagnosis")
async def diagnosis(
    user: user_dependency, diagnosis_request: DiagnosisRequest, db: db_dependency
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    
    kondisi = diagnosis_request.kondisi
    threshold = diagnosis_request.threshold

    penyakit_cf = {}  # dictionary untuk menyimpan CF penyakit

    # Mendapatkan daftar gejala dari database
    gejala_dict = {}
    for gejala in db.query(Gejala).all():
        gejala_dict[str(gejala.id)] = gejala.nama  # Menggunakan ID sebagai string untuk memastikan kesesuaian dengan kunci dalam data permintaan


    # Hitung CF untuk setiap penyakit berdasarkan gejala
    for penyakit in db.query(Penyakit).all():
        cf_total_temp = Decimal(0)
        cf_total_temp = cf_total_temp.quantize(Decimal('0.00'))
        gejala_penyakit = []  # Menyimpan gejala untuk setiap penyakit
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

                gejala_obj = db.query(Gejala).filter(Gejala.id == gejala_id).first()
                gejala_penyakit.append(gejala_obj.nama)

        if cf_total_temp > threshold:
            # Membatasi hanya dua angka di belakang koma
            cf_total_temp = cf_total_temp.quantize(Decimal('0.00'))
            penyakit_cf[penyakit.nama] = {
                "gejala": gejala_penyakit,
                "kemungkinan": round(float(cf_total_temp) * 100, 2),  # Ubah ke persentase
                "detail": penyakit.detail,
                "saran": penyakit.saran,
                "gambar": penyakit.gambar
            }
            
            # Simpan hasil perhitungan ke dalam tabel Hasil
            hasil = Hasil(
                penyakit=penyakit.nama,
                gejala=', '.join(gejala_penyakit),
                nilai=f"{round(float(cf_total_temp) * 100, 2)}%",  # Ubah ke persentase
                tanggal=datetime.now()
            )
            db.add(hasil)
            db.commit()
    
    # Urutkan penyakit berdasarkan keyakinan (CF) dari yang tertinggi
    sorted_penyakit_cf = dict(sorted(penyakit_cf.items(), key=lambda item: item[1]["kemungkinan"], reverse=True))

    # Buat respons diagnosis
    diagnosis_response = []
    for penyakit, info in sorted_penyakit_cf.items():
        # Ubah ID gejala menjadi nama gejala
        gejala_with_name = [{'gejala_id': gejala_id, 'bobot': bobot, 'nama_gejala': gejala_dict[gejala_id]} 
                            for gejala_id, bobot in zip([gejala['gejala_id'] for gejala in kondisi], 
                                                        [gejala['bobot'] for gejala in kondisi])]
        diagnosis_request_with_name = DiagnosisRequest(kondisi=gejala_with_name, threshold=diagnosis_request.threshold)
        diagnosis_response.append(DiagnosisResponse(
            penyakit=penyakit,
            gejala=info["gejala"],
            kemungkinan=f"{info['kemungkinan']}%",
            detail=info["detail"],
            saran=info["saran"],
            gambar=info["gambar"],
            request_data=diagnosis_request_with_name  # Masukkan data permintaan diagnosa ke respons
        ))

    return diagnosis_response

