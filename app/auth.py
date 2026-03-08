# IMPORTS ---------------------------------------------------
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

# ATENÇÃO, em produção essa chave deve vir de uma variável de ambiente,
# nunca hardcoded no código. Qualquer pessoa com acesso ao repositório
# conseguiria forjar tokens válidos se essa chave vazar.
SECRET_KEY = "stockflow-skey-dev"

# HS256 é o algoritmo de assinatura do JWT, simétrico, usa a mesma
# chave para assinar e verificar.
ALGORITHM = "HS256"

# Tokens expiram em 60 minutos. Após isso o usuário precisa logar novamente.
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Contexto de criptografia usando bcrypt.
# deprecated="auto" atualiza automaticamente hashes antigos para
# versões mais seguras do algoritmo quando o usuário logar.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Define que o token deve vir no header Authorization: Bearer <token>.
oauth2_scheme = HTTPBearer()


def hash_password(password: str) -> str:
    # Transforma a senha em um hash irreversível antes de salvar no banco.
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    # Compara a senha digitada com o hash salvo, sem precisar reverter o hash.
    return pwd_context.verify(plain, hashed)


def create_token(data: dict) -> str:
    payload = data.copy()

    # Adiciona a data de expiração ao payload antes de assinar.
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload["exp"] = expire

    # jwt.encode assina o payload com a SECRET_KEY e retorna a string do token.
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# Dependência injetada nas rotas protegidas.
# Extrai e valida o token JWT de cada requisição antes de executar a rota.
# Se o token for inválido, expirado ou o usuário não existir, retorna 401.
def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        db: Session = Depends(get_db)
):
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado!",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials

        # Decodifica e valida a assinatura do token.
        # Lança JWTError se o token for inválido ou expirado.
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # sub (subject) é a convenção JWT para identificar o dono do token.
        username: str = payload.get("sub")
        if username is None:
            raise credentials_error
    except JWTError:
        raise credentials_error

    # Confirma que o usuário ainda existe no banco.
    # Cobre o caso de um token válido para um usuário que foi deletado.
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_error
    return user