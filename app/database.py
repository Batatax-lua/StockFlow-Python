# IMPORTS ---------------------------------------------------
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Lê a URL do banco da variável de ambiente DATABASE_URL.
# Em desenvolvimento local, usa SQLite como fallback, sem precisar instalar nada.
# Em produção (Docker, Render), a variável aponta para o PostgreSQL.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./stockflow.db"
)

# O SQLite exige check_same_thread=False para funcionar com o FastAPI,
# que usa múltiplas threads. O PostgreSQL não tem essa restrição,
# então o argumento é passado só quando necessário.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Engine é a conexão física com o banco, criada uma vez e reutilizada.
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# SessionLocal é uma fábrica de sessões. Cada requisição abre uma sessão
# nova, usa para ler ou escrever, e fecha ao terminar.
# autocommit=False exige que o commit seja chamado explicitamente,
# dando controle total sobre quando as mudanças são confirmadas.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base é a classe mãe de todos os models. Qualquer classe que herdar dela
# é reconhecida pelo SQLAlchemy como uma tabela do banco.
Base = declarative_base()

# Dependência injetada pelo FastAPI em cada rota que precisar do banco.
# O yield abre a sessão, pausa para a rota executar, e o finally
# garante que a sessão seja fechada mesmo que ocorra um erro.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()