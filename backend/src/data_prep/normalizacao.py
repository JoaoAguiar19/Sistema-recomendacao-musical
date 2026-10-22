import pandas as pd
from sklearn.preprocessing import MinMaxScaler

in_path = 'data/processed/dataset_limpo.csv'
out_path = 'data/processed/dataset_normalizado.csv'

features = [
    'tempo', 'loudness', 'valence', 'energy', 
    'danceability', 'speechiness', 'acousticness', 
    'instrumentalness', 'liveness'
]

df = pd.read_csv(in_path)

scaler = MinMaxScaler()
df[features] = scaler.fit_transform(df[features])

df.to_csv(out_path, index=False)

print(f"Normalização concluída: {out_path}\n")
print(df[['track_name', 'tempo', 'energy', 'valence']].head())