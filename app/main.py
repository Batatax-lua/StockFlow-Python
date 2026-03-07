from fastapi import FastAPI
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StockFlow",
    description="API de PDV e gestão de estoque",
    version="0.0.1"
)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "StockFlow is running"}