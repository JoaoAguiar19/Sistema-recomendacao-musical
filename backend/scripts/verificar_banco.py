import pandas as pd
from sqlalchemy import text
from core.database import engine

print("=== DIAGNÓSTICO DA TABELA 'MUSICAS' NO POSTGRESQL ===")

with engine.connect() as conexao:
    total_registros = conexao.execute(text("SELECT COUNT(*) FROM musicas")).scalar()
    print(f"Total de músicas cadastradas no PostgreSQL: {total_registros}\n")

    df_amostra = pd.read_sql("SELECT * FROM musicas LIMIT 3", engine)
    colunas_banco = list(df_amostra.columns)
    
    print(f"Colunas ativas na tabela 'musicas': {colunas_banco}\n")

    colunas_obrigatorias = ['popularity', 'track_genre', 'key', 'mode']
    ausentes = [col for col in colunas_obrigatorias if col not in colunas_banco]

    if ausentes:
        print(f"ERRO DE SCHEMA: As colunas {ausentes} não existem na tabela 'musicas'.")
        print("Execute 'python3 -m src.data_prep.inserir_banco' para recriar a estrutura.")
    else:
        print("Validação concluída com sucesso! Todas as colunas necessárias para o A* estão no PostgreSQL.")