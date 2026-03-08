from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas, auth

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

limiter = Limiter(key_func=get_remote_address)

@router.post("/register", response_model=schemas.UserResponse, status_code=201)
@limiter.limit("5/minute")
def register(request: Request, user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username já existe")
    
    new_user = models.User(
        username=user.username,
        hashed_password=auth.hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=schemas.Token)
@limiter.limit("10/minute")
def login(request: Request, user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Usuário ou senha incorretos")
    
    token = auth.create_token(data={"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}