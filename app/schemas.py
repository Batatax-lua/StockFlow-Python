# IMPORTS ---------------------------------------------------
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# PRODUTOS --------------------------------------------------

# Dados esperados ao criar um produto.
# name e price são obrigatórios, description e stock são opcionais.
class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int = 0

# Dados aceitos ao atualizar um produto.
# Todos os campos são opcionais para permitir atualizações parciais,
# ou seja, mandar só o preço sem precisar repetir nome e estoque.
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None

# Formato do produto retornado pela API.
# Inclui id e created_at, que são gerados pelo banco e nunca enviados pelo cliente.
class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    stock: int
    created_at: datetime

    class Config:
        # Permite que o Pydantic leia objetos do SQLAlchemy diretamente,
        # sem precisar converter manualmente para dicionário.
        from_attributes = True

# ITENS DE VENDA --------------------------------------------

# Dados esperados para cada item ao criar uma venda.
# unit_price não é enviado pelo cliente, o sistema busca do cadastro do produto.
class SaleItemCreate(BaseModel):
    product_id: int
    quantity: int

# Formato do item retornado pela API.
# product_id é Optional porque o produto pode ter sido deletado depois da venda,
# nesse caso o campo fica None mas o histórico da venda é preservado.
class SaleItemResponse(BaseModel):
    id: int
    product_id: Optional[int] = None
    quantity: int
    unit_price: float

    class Config:
        from_attributes = True

# VENDAS ----------------------------------------------------

# Dados esperados ao criar uma venda.
# O cliente manda apenas a lista de itens, o total é calculado pelo sistema.
class SaleCreate(BaseModel):
    items: list[SaleItemCreate]

# Formato da venda retornada pela API, incluindo todos os itens associados.
class SaleResponse(BaseModel):
    id: int
    total: float
    created_at: datetime
    items: list[SaleItemResponse]

    class Config:
        from_attributes = True

# USUÁRIOS --------------------------------------------------

# Dados esperados ao registrar ou fazer login.
class UserCreate(BaseModel):
    username: str
    password: str

# Formato do usuário retornado pela API.
# Nunca inclui a senha, nem o hash dela.
class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime

    class Config:
        from_attributes = True

# Formato do token retornado após login bem-sucedido.
class Token(BaseModel):
    access_token: str
    token_type: str