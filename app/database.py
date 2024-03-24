from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Ganti informasi koneksi sesuai dengan database MySQL Anda
DB_USER = "root"
DB_PASSWORD = "Seman123"
DB_HOST = "localhost"
DB_PORT = "3307"
DB_NAME = "pakar_ayam"

# Format URL koneksi MySQL
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Buat engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Buat session lokal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Buat base deklaratif
Base = declarative_base()
