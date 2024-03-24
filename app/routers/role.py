from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from app.models import Role
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

class RoleBase(BaseModel):
    role: str

class RoleCreate(RoleBase):
    pass

class RoleResponse(BaseModel):
    id: int
    role: str

class RoleUpdate(BaseModel):
    role: Optional[str] = None

@router.get("/role", response_model=List[RoleResponse])
async def read_all_roles(user: user_dependency, db: db_dependency):
    roles = db.query(Role).all()
    return roles

@router.post("/role/store", response_model=RoleResponse)
async def create_role(role_create: RoleCreate, db: db_dependency, user: user_dependency):
    role_db = Role(role=role_create.role)
    db.add(role_db)
    db.commit()
    db.refresh(role_db)
    return role_db

@router.put("/role/update/{role_id}", response_model=RoleResponse)
async def update_role(role_id: int, role_update: RoleUpdate, db: db_dependency, user: user_dependency):
    role = db.query(Role).filter(Role.id == role_id).first()
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")

    for key, value in role_update.dict(exclude_unset=True).items():
        setattr(role, key, value)
    db.commit()
    db.refresh(role)
    return role

@router.delete("/role/delete/{role_id}")
async def delete_role(role_id: int, db: db_dependency, user: user_dependency):
    role = db.query(Role).filter(Role.id == role_id).first()
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    db.delete(role)
    db.commit()
    return {"message": "Role deleted successfully"}
