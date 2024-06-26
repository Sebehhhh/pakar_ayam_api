from fastapi import FastAPI
import app.models as models
from app.database import engine
from app.routers import auth,homepage, gejala, users, role, penyakit, basis_pengetahuan, hasil # Merubah users menjadi user

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(gejala.router)
app.include_router(penyakit.router)
app.include_router(basis_pengetahuan.router)
app.include_router(hasil.router)
app.include_router(homepage.router)
app.include_router(users.router)
app.include_router(role.router)
