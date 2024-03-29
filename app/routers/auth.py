from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import Annotated
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status
from jose import jwt, JWTError
from datetime import datetime, timedelta

from app.models import User  # Menggunakan model User yang telah diperbarui
from app.database import SessionLocal

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = "fe71370dc5937b6b06531b09eae3632f530b229c6c409fa8769671045da31cba"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")

class CreateUserRequest(BaseModel):
    username: str
    nama: str
    password: str
    role_id: int

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str
    role_id: int

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.password):
        return False
    return user

def create_access_token(username: str, user_id: int, role_id: int, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id, "role_id": role_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        role_id: int = payload.get("role_id")
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user.",
            )
        return {"username": username, "id": user_id, "role_id": role_id}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user."
        )

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user.",
        )

    token = create_access_token(
        user.username, user.id, user.role_id, timedelta(minutes=60*24)
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "role_id": user.role_id
    }

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    # Di sini Anda dapat menambahkan logika tambahan, seperti pencatatan aktivitas logout, dll.
    return {"message": "Logged out successfully"}, status.HTTP_200_OK
