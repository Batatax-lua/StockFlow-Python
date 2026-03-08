# IMPORTS ---------------------------------------------------
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

# Cada classe que herda de Base vira uma tabela no banco.
# O SQLAlchemy usa essas definições para criar as tabelas
# e para mapear objetos Python para linhas do banco.

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamento com SaleItem, permite acessar product.sale_items
    # para ver todas as vezes que esse produto apareceu em vendas.
    sale_items = relationship("SaleItem", back_populates="product")


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    total = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamento com SaleItem, permite acessar sale.items
    # para ver todos os produtos de uma venda específica.
    items = relationship("SaleItem", back_populates="sale")


class SaleItem(Base):
    # Tabela intermediária que representa um produto dentro de uma venda.
    # Existe porque uma venda pode ter vários produtos e um produto
    # pode aparecer em várias vendas, uma relação muitos-para-muitos.
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer, nullable=False)

    # Preço salvo no momento da venda, não referenciado do produto.
    # Garante que alterações futuras de preço não mudem o histórico.
    unit_price = Column(Float, nullable=False)

    # ondelete="SET NULL" define o comportamento ao deletar um produto,
    # em vez de bloquear a exclusão, coloca NULL aqui e preserva o histórico.
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)

    product = relationship("Product", back_populates="sale_items")
    sale = relationship("Sale", back_populates="items")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)

    # Nunca armazenamos a senha original, apenas o hash gerado pelo bcrypt.
    # A verificação no login compara hashes, não senhas em texto puro.
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)