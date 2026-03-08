# IMPORTS ---------------------------------------------------
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

# Limiter local para aplicar rate limiting nas rotas de autenticação.
# Rotas de login e registro são as mais vulneráveis a ataques de força bruta,
# por isso recebem limites mais restritivos que o resto da API.
limiter = Limiter(key_func=get_remote_address)


@router.post("/register", response_model=schemas.UserResponse, status_code=201)
@limiter.limit("5/minute")  # máximo 5 cadastros por minuto por IP
def register(request: Request, user: schemas.UserCreate, db: Session = Depends(get_db)):
    # request é obrigatório como primeiro parâmetro para o slowapi
    # conseguir identificar o IP de quem fez a requisição.
    existing = db.query(models.User).filter(models.User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username já existe")

    new_user = models.User(
        username=user.username,
        # A senha é hasheada antes de salvar, nunca armazenamos texto puro.
        hashed_password=auth.hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=schemas.Token)
@limiter.limit("10/minute")  # máximo 10 tentativas de login por minuto por IP
def login(request: Request, user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()

    # A verificação de usuário inexistente e senha incorreta retorna o mesmo
    # erro intencionalmente, evitando que um atacante descubra quais
    # usernames existem no sistema através das mensagens de erro.
    if not db_user or not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Usuário ou senha incorretos")

    # sub (subject) é a convenção JWT para identificar o dono do token.
    token = auth.create_token(data={"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}