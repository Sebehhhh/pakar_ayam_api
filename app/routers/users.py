from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from app.models import Role, User
from app.database import SessionLocal
from .auth import get_current_user

router = APIRouter()

# Hashing password
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class UserBase(BaseModel):
    nama: str
    username: str
    password: str
    role_id: int

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    nama: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    role_id: Optional[int] = None
    
class UserResponse(BaseModel):
    id: int
    nama: str
    username: str
    role_id: int
    role_name: str
    
@router.get("/user", response_model=List[UserResponse])
async def read_all_users(user: user_dependency, db: db_dependency):
    users = db.query(User).all()
    user_responses = []
    for user in users:
        role = db.query(Role).filter(Role.id == user.role_id).first()
        role_name = role.role if role else None
        user_response = UserResponse(
            id=user.id,
            nama=user.nama,
            username=user.username,
            role_id=user.role_id,
            role_name=role_name
        )
        user_responses.append(user_response)
    return user_responses

@router.post("/user/store", response_model=UserBase)
async def create_user(user_create: UserCreate, db: db_dependency, user: user_dependency):
    hashed_password = bcrypt_context.hash(user_create.password)
    user_db = User(
        nama=user_create.nama,
        username=user_create.username,
        password=hashed_password, 
        role_id=user_create.role_id
        )
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return user_db

@router.put("/user/update/{user_id}", response_model=UserBase)
async def update_user(user_id: int, user_update: UserUpdate, db: db_dependency, user: user_dependency):
    # Mengambil data pengguna dari database
    user_db = db.query(User).filter(User.id == user_id).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="Pengguna tidak ditemukan")
    
    # Memperbarui informasi pengguna
    if user_update.password:
        hashed_password = bcrypt_context.hash(user_update.password)
        user_db.password = hashed_password
    if user_update.nama:
        user_db.nama = user_update.nama
    if user_update.username:
        user_db.username = user_update.username
    if user_update.role_id:
        user_db.role_id = user_update.role_id
    
    # Melakukan commit perubahan ke database
    db.commit()
    db.refresh(user_db)
    
    return user_db

@router.delete("/user/delete/{user_id}")
async def delete_user(user_id: int, db: db_dependency, user: user_dependency):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}
