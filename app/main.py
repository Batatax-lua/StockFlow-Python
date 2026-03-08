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

Base.metadata.create_all(bind=engine)

IS_PROD = os.getenv("ENVIRONMENT") == "production"

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="StockFlow",
    description="API de PDV e gestão de estoque",
    version="0.1.0",
    docs_url=None if IS_PROD else "/docs",
    redoc_url=None if IS_PROD else "/redoc"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router, dependencies=[Depends(get_current_user)])
app.include_router(sales.router, dependencies=[Depends(get_current_user)])
app.include_router(dashboard.router, dependencies=[Depends(get_current_user)])

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "StockFlow is running"}