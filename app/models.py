from sqlalchemy import Column, Float, DateTime, Text, Integer, String, ForeignKey
from app.database import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(20), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    nama = Column(String(30), nullable=False)
    role_id = Column(Integer, ForeignKey("role.id"))

class Gejala(Base):
    __tablename__ = "gejala"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String(50), nullable=False,unique=True)

class Role(Base):
    __tablename__ = "role"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(30), nullable=False,unique=True)
    
class Penyakit(Base):
    __tablename__ = "penyakit"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String(50), nullable=False,unique=True)
    detail = Column(Text, nullable=False)
    saran = Column(Text, nullable=True)
    gambar = Column(Text, nullable=True)

class BasisPengetahuan(Base):
    __tablename__ = "basis_pengetahuan"

    id = Column(Integer, primary_key=True, index=True)
    penyakit_id = Column(Integer, ForeignKey("penyakit.id"))
    gejala_id = Column(Integer, ForeignKey("gejala.id"))
    mb = Column(Float(11, 1))
    md = Column(Float(11, 1))
    