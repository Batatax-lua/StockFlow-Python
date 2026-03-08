from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from app.routes import products, sales, auth, dashboard
from app.auth import get_current_user

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StockFlow",
    description="API de PDV e gestão de estoque",
    version="0.0.1"
)

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