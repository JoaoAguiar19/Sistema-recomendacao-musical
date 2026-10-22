import pandas as pd

raw_path = 'data/raw/dataset.csv'
out_path = 'data/processed/dataset_limpo.csv'

df = pd.read_csv(raw_path)

# Limpeza encadeada (mais idiomático em Pandas)
df_limpo = (
    df.drop(columns=['Unnamed: 0'], errors='ignore')
      .drop_duplicates(subset=['track_id'])
      .drop_duplicates(subset=['track_name', 'artists'])
      .dropna(subset=['tempo', 'valence', 'energy', 'danceability'])
)

df_limpo.to_csv(out_path, index=False)

print(f"Limpeza concluída: {len(df_limpo)} registros salvos.")