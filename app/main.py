# IMPORTS ---------------------------------------------------
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.database import engine, Base
from app.routes import products, sales, auth, dashboard
from app.auth import get_current_user
import os

# Cria todas as tabelas no banco ao iniciar, caso ainda não existam.
# O SQLAlchemy verifica antes de criar, não sobrescreve dados existentes.
Base.metadata.create_all(bind=engine)

# Lê a variável de ambiente ENVIRONMENT.
# Em produção (Render), essa variável é setada como "production".
# Em desenvolvimento local, ela não existe, IS_PROD fica False.
IS_PROD = os.getenv("ENVIRONMENT") == "production"

# Limiter identifica cada cliente pelo IP da requisição,
# usado para aplicar rate limiting nas rotas de autenticação.
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="StockFlow",
    description="API de PDV e gestão de estoque",
    version="0.1.0",
    # Desativa a documentação interativa em produção.
    # /docs e /redoc expõem a estrutura da API, úteis em dev mas arriscado em produção
    docs_url=None if IS_PROD else "/docs",
    redoc_url=None if IS_PROD else "/redoc"
)

# Registra o limiter no estado global do app para que os decorators
# @limiter.limit() nas rotas consigam acessá-lo.
app.state.limiter = limiter

# Quando o rate limit é excedido, retorna 429 (Too Many Requests)
# em vez de deixar estourar um erro 500.
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS permite que o frontend faça requisições para a API
# mesmo estando em domínios diferentes.
# allow_origins=["*"] libera qualquer origem. Em produção mais restrita,
# isso seria substituído pelo domínio específico do frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROTAS -----------------------------------------------------

# Rotas de autenticação ficam abertas, sem exigir token.
# Qualquer um pode se registrar e fazer login.
app.include_router(auth.router)

# Rotas de negócio são protegidas.
# O Depends(get_current_user) é executado antes de qualquer rota desses routers,
# se o token for inválido ou ausente, a requisição é bloqueada com 401.
app.include_router(products.router, dependencies=[Depends(get_current_user)])
app.include_router(sales.router, dependencies=[Depends(get_current_user)])
app.include_router(dashboard.router, dependencies=[Depends(get_current_user)])

# Endpoint de health check, usado pelo Render para monitorar se o serviço
# está respondendo. Precisa estar registrado antes do mount do frontend,
# caso contrário o StaticFiles intercepta a rota primeiro.
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "StockFlow is running"}

# Serve os arquivos estáticos do frontend.
# O mount em "/" deve sempre vir por último, ele captura todas as rotas
# não registradas anteriormente, funcionando como fallback.
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")