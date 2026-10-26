import pandas as pd
from core.database import engine

caminho_csv = 'data/processed/dataset_normalizado.csv'
df = pd.read_csv(caminho_csv)

print(f"Colunas lidas do CSV: {list(df.columns)}")

# 1. Lista de colunas exigidas na tabela do PostgreSQL
colunas_banco = [
    'track_id', 'track_name', 'artists', 'track_genre', 'popularity',
    'key', 'mode', 'tempo', 'valence', 'energy', 'danceability',
    'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness'
]

# Filtra mantendo apenas as colunas mapeadas que existem no CSV
colunas_presentes = [col for col in colunas_banco if col in df.columns]
df_banco = df[colunas_presentes].copy()

# 2. Filtro por popularidade mínima
if 'popularity' in df_banco.columns:
    df_banco = df_banco[df_banco['popularity'] >= 30]

# 3. Amostragem segura sem perder a coluna 'track_genre'
qtd_por_genero = 200

if 'track_genre' in df_banco.columns:
    subconjuntos = []
    for genero, grupo in df_banco.groupby('track_genre'):
        qtd = min(len(grupo), qtd_por_genero)
        subconjuntos.append(grupo.sample(n=qtd, random_state=42))
    
    df_amostra = pd.concat(subconjuntos, ignore_index=True)
else:
    df_amostra = df_banco

print(f"Total selecionado: {len(df_amostra)} músicas.")
print(f"Colunas a serem salvas no PostgreSQL: {list(df_amostra.columns)}")

# 4. Substitui a tabela 'musicas' no Neon
df_amostra.to_sql(
    name='musicas',
    con=engine,
    if_exists='replace',
    index=False,
    chunksize=1000
)

print("Tabela 'musicas' atualizada com sucesso no PostgreSQL!")