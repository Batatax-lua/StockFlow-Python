# ⚡ StockFlow

Sistema de ponto de venda e gestão de estoque desenvolvido com Python e FastAPI.

🔗 **[Acesse o sistema](https://stockflow-python.onrender.com)**

---
## Funcionalidades

- Cadastro e gerenciamento de produtos com controle de estoque
- Registro de vendas com múltiplos itens
- Dashboard com faturamento total, vendas e produtos mais vendidos
- Alertas de estoque baixo
- Histórico de vendas com filtro por data
- Autenticação JWT com proteção de rotas
- Rate limiting para proteção contra abuso

## Tecnologias

**Backend**
- Python 3.11
- FastAPI
- SQLAlchemy (ORM)
- PostgreSQL
- JWT (autenticação)

**Frontend**
- HTML, CSS e JavaScript

**Infraestrutura**
- Docker + Docker Compose
- Deploy no Render

## Como rodar localmente

**Pré-requisitos:** Docker instalado
```bash
git clone https://github.com/Batatax-lua/StockFlow-Python
cd StockFlow-Python
docker compose up --build
```

Acesse `http://localhost:8000`

## Estrutura do projeto
```
stockflow/
├── app/
│   ├── main.py        # Entry point
│   ├── models.py      # Tabelas do banco
│   ├── schemas.py     # Validação de dados
│   ├── auth.py        # JWT e autenticação
│   └── routes/        # Rotas da API
├── frontend/
│   └── index.html     # Interface web
├── Dockerfile
└── docker-compose.yml
```
