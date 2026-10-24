import pandas as pd
from core.database import engine

caminho_csv = 'data/processed/dataset_normalizado.csv'
df = pd.read_csv(caminho_csv)

# 1. Filtra o dataset para conter apenas as colunas mapeadas no banco de dados
colunas_banco = [
    'track_id', 'track_name', 'artists', 'track_genre',
    'tempo', 'valence', 'energy', 'danceability', 'loudness',
    'speechiness', 'acousticness', 'instrumentalness', 'liveness'
]
df = df[colunas_banco]

# 2. Separa as amostras por gênero
qtd_por_genero = 50

df_amostra = df.groupby('track_genre').apply(
    lambda x: x.sample(n=min(len(x), qtd_por_genero), random_state=42)
).reset_index(drop=True)

print(f"Total selecionado: {len(df_amostra)} músicas.")
print("A iniciar inserção no banco PostgreSQL...")

# 3. Insere no banco
df_amostra.to_sql(
    name='musicas', 
    con=engine, 
    if_exists='append', 
    index=False, 
    chunksize=1000
)

print("Inserção concluída com sucesso!")