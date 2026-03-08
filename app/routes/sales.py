from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from datetime import datetime

router = APIRouter(
    prefix="/sales",
    tags=["Sales"]
)

@router.post("/", response_model=schemas.SaleResponse, status_code=201)
def create_sale(sale: schemas.SaleCreate, db: Session = Depends(get_db)):
    total = 0.0
    sale_items = []

    for item in sale.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()

        if not product:
            raise HTTPException(status_code=404, detail=f"Produto {item.product_id} não encontrado!")
        
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Estoque insuficiente do produto '{product.name}'. Estoque disponível: {product.stock}")
        
        product.stock -= item.quantity

        subtotal = product.price * item.quantity
        total += subtotal

        sale_items.append(models.SaleItem(
            product_id=product.id,
            quantity=item.quantity,
            unit_price=product.price
        ))

    new_sale = models.Sale(total=total)
    db.add(new_sale)
    db.flush()

    for sale_item in sale_items:
        sale_item.sale_id = new_sale.id
        db.add(sale_item)

    db.commit()
    db.refresh(new_sale)

    db.expire(new_sale)
    new_sale = db.query(models.Sale).filter(models.Sale.id == new_sale.id).first()
    return new_sale

@router.get("/", response_model=list[schemas.SaleResponse])
def list_sales(db: Session = Depends(get_db)):
    sales = db.query(models.Sale).all()
    return sales

@router.get("/history", response_model=list[schemas.SaleResponse])
def sale_history(
    start: str = None,
    end: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Sale)

    if start:
        try:
            start_date = datetime.strptime(start, "%d-%m-%Y")
            query = query.filter(models.Sale.created_at >= start_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de data incorreto. Use DD-MM-YYYY")
        
    if end:
        try:
            end_date = datetime.strptime(end, "%d-%m-%Y").replace(hour=23, minute=59, second=59)
            query = query.filter(models.Sale.created_at <= end_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de data incorreto. Use DD-MM-YYYY")
    
    return query.order_by(models.Sale.created_at.desc()).all()

@router.get("/{sale_id}", response_model=schemas.SaleResponse)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    sale = db.query(models.Sale).filter(models.Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Venda não encontrada!")
    return sale

