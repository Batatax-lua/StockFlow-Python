# IMPORTS ---------------------------------------------------
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from datetime import datetime

router = APIRouter(
    prefix="/sales",
    tags=["Sales"]
)

# ROTAS -----------------------------------------------------
@router.post("/", response_model=schemas.SaleResponse, status_code=201)
def create_sale(sale: schemas.SaleCreate, db: Session = Depends(get_db)):
    total = 0.0
    sale_items = []

    # Valida e processa cada item antes de salvar qualquer coisa.
    # Se um item falhar, nenhuma alteração é confirmada no banco,
    # garantindo que a venda seja criada completa ou não seja criada.
    for item in sale.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()

        if not product:
            raise HTTPException(status_code=404, detail=f"Produto {item.product_id} não encontrado!")
        
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Estoque insuficiente do produto '{product.name}'. Estoque disponível: {product.stock}")
        
        # Desconta o estoque. O SQLAlchemy rastreia a mudança automaticamente
        # e a persiste no banco quando o commit for chamado.
        product.stock -= item.quantity

        subtotal = product.price * item.quantity
        total += subtotal

        # O preço unitário é salvo no momento da venda, não referenciado
        # do produto. Isso garante que alterações futuras de preço não
        # afetem o histórico de vendas anteriores.
        sale_items.append(models.SaleItem(
            product_id=product.id,
            quantity=item.quantity,
            unit_price=product.price
        ))

    new_sale = models.Sale(total=total)
    db.add(new_sale)

    # flush envia as mudanças para o banco sem confirmar a transação,
    # o suficiente para o banco gerar o ID da venda.
    # Esse ID é necessário para associar os itens à venda logo abaixo.
    db.flush()

    for sale_item in sale_items:
        sale_item.sale_id = new_sale.id
        db.add(sale_item)

    db.commit()
    db.refresh(new_sale)

    # O refresh sozinho nem sempre carrega os relacionamentos após o commit.
    # O expire força o SQLAlchemy a descartar o cache do objeto, e a query
    # seguinte recarrega a venda com todos os itens do banco.
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
    # Começa com todas as vendas e aplica os filtros conforme os parâmetros
    # recebidos. Se nenhum for enviado, retorna o histórico completo.
    query = db.query(models.Sale)

    if start:
        try:
            start_date = datetime.strptime(start, "%d-%m-%Y")
            query = query.filter(models.Sale.created_at >= start_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de data incorreto. Use DD-MM-YYYY")
        
    if end:
        try:
            # replace garante que o filtro inclui o dia inteiro até 23:59:59,
            # evitando que vendas do próprio dia sejam excluídas.
            end_date = datetime.strptime(end, "%d-%m-%Y").replace(hour=23, minute=59, second=59)
            query = query.filter(models.Sale.created_at <= end_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de data incorreto. Use DD-MM-YYYY")
    
    # Ordena da mais recente para a mais antiga.
    return query.order_by(models.Sale.created_at.desc()).all()


@router.get("/{sale_id}", response_model=schemas.SaleResponse)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    # Essa rota deve sempre ficar por último no arquivo.
    # O FastAPI testa rotas na ordem de registro, então rotas estáticas
    # como /history precisam vir antes desta para não serem capturadas
    # pelo parâmetro dinâmico {sale_id}.
    sale = db.query(models.Sale).filter(models.Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Venda não encontrada!")
    return sale