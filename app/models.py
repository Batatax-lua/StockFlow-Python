from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.now(datetime.timezone.utc))

    sale_items = relationship("SaleItem", back_populates="product")

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    total = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.now(datetime.timezone.utc))

    items = relationship("SaleItem", back_populates="sale")

class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, Index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)

    product = relationship("Product", back_populates="sale_items")
    sale = relationship("Sale", back_populates="items")