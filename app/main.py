from fastapi import FastAPI, Depends
from app.database import engine, Base
from app.routes import products, sales, auth
from app.auth import get_current_user

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StockFlow",
    description="API de PDV e gestão de estoque",
    version="0.0.1"
)

app.include_router(auth.router)
app.include_router(products.router, dependencies=[Depends(get_current_user)])
app.include_router(sales.router, dependencies=[Depends(get_current_user)])

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "StockFlow is running"}