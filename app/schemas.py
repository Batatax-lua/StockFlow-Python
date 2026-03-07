from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Produtos -------------------------------

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int = 0

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[str] = None
    stock: Optional[str] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    stock: int
    created_at: datetime

    class Config:
        from_attributes = True

# SaleItems ------------------------------

class SaleItemCreate(BaseModel):
    product_id: int
    quantity: int

class SaleItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float

    class Config:
        from_attributes = True

# Sale -----------------------------------

class SaleCreate(BaseModel):
    items: list[SaleItemCreate]

class SaleResponse(BaseModel):
    id: int
    total: float
    created_at: datetime
    items: list[SaleItemResponse]

    class Config:
        from_attributes = True
        