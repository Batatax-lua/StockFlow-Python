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
    total_revenue = db.query(func.sum(models.Sale.total)).scalar() or 0.0
    total_sales = db.query(func.count(models.Sale.id)).scalar() or 0.0
    total_products = db.query(func.count(models.Product.id)).scalar() or 0.0

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
        "top_products": [
            {"name": name, "total_sold": total_sold}
            for name, total_sold in top_products
        ]
    }