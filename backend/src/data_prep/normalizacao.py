import pandas as pd
import joblib
from sklearn.preprocessing import MinMaxScaler

in_path = 'data/processed/dataset_limpo.csv'
out_path = 'data/processed/dataset_normalizado.csv'
scaler_path = 'data/processed/scaler.pkl'

features = [
    'tempo', 'loudness', 'valence', 'energy', 
    'danceability', 'speechiness', 'acousticness', 
    'instrumentalness', 'liveness'
]

df = pd.read_csv(in_path)

scaler = MinMaxScaler()
df[features] = scaler.fit_transform(df[features])

df.to_csv(out_path, index=False)
joblib.dump(scaler, scaler_path)

print(f"Dataset salvo em: {out_path}")
print(f"Modelo matemático salvo em: {scaler_path}")