from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from core.database import engine, Base, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API - Recomendação Musical por Grafos")

@app.get("/")
def read_root():
    return {"mensagem": "API de Recomendação Musical a funcionar!"}

@app.get("/teste-db")
def testar_conexao(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "Sucesso", "mensagem": "Conectado ao PostgreSQL perfeitamente!"}
    except Exception as e:
        return {"status": "Erro", "mensagem": str(e)}
