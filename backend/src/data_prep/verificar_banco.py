from sqlalchemy import text
from core.database import engine

with engine.connect() as conn:
    resultado = conn.execute(text("SELECT COUNT(*) FROM musicas")).scalar()
    print(f"Total de músicas no banco PostgreSQL: {resultado}")