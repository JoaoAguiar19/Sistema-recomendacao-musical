import os
import pandas as pd
from core.database import engine

# Mapeamento dinâmico de caminhos
DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(DIRETORIO_ATUAL) 
caminho_csv = os.path.join(BASE_DIR, 'data', 'processed', 'dataset_normalizado.csv')

print("A carregar dataset normalizado...")
df = pd.read_csv(caminho_csv)

# 1. Colunas exigidas na tabela do PostgreSQL
colunas_banco = [
    'track_id', 'track_name', 'artists', 'track_genre', 'popularity',
    'key', 'mode', 'tempo', 'valence', 'energy', 'danceability',
    'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness'
]

colunas_presentes = [col for col in colunas_banco if col in df.columns]
df_banco = df[colunas_presentes].copy()

# 2. Amostragem Aleatória Global de Alta Qualidade (ex: 25.000 músicas)
# Garante um grafo robusto para o A* sem estourar a memória RAM ou o Neon
TAMANHO_AMOSTRA = 25000

if len(df_banco) > TAMANHO_AMOSTRA:
    df_amostra = df_banco.sample(n=TAMANHO_AMOSTRA, random_state=42)
else:
    df_amostra = df_banco

print(f"Total selecionado para o banco (amostra global): {len(df_amostra):,} músicas.")

# 3. Envio para o PostgreSQL (Neon)
print("A enviar dados para o PostgreSQL (Neon)...")
df_amostra.to_sql(
    name='musicas',
    con=engine,
    if_exists='replace',
    index=False,
    chunksize=2000
)

print("✅ Tabela 'musicas' atualizada com sucesso no PostgreSQL!")