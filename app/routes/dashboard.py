# IMPORTS ---------------------------------------------------
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app import models

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

@router.get("/")
def get_dashboard(db: Session = Depends(get_db)):
    # func é a forma do SQLAlchemy chamar funções SQL como SUM e COUNT.
    # .scalar() retorna um único valor em vez de uma lista de resultados.
    # O "or 0" garante que retorna zero quando não há dados, evitando None.
    total_revenue = db.query(func.sum(models.Sale.total)).scalar() or 0.0
    total_sales = db.query(func.count(models.Sale.id)).scalar() or 0.0
    total_products = db.query(func.count(models.Product.id)).scalar() or 0.0

    # Busca os 5 produtos mais vendidos em quantidade, somando todos os
    # itens de todas as vendas. O JOIN liga produtos aos seus itens de venda,
    # e o GROUP BY agrupa os resultados por produto antes de somar.
    top_products = (
        db.query(
            models.Product.name,
            func.sum(models.SaleItem.quantity).label("total_sold")
        )
        .join(models.SaleItem, models.Product.id == models.SaleItem.product_id)
        .group_by(models.Product.id)
        .order_by(func.sum(models.SaleItem.quantity).desc())
        .limit(5)
        .all()
    )

    return {
        "total_revenue": round(total_revenue, 2),
        "total_sales": total_sales,
        "total_products": total_products,
        # Converte a lista de tuplas (name, total_sold) retornada pelo SQLAlchemy
        # em uma lista de dicionários legível pelo frontend.
        "top_products": [
            {"name": name, "total_sold": total_sold}
            for name, total_sold in top_products
        ]
    }