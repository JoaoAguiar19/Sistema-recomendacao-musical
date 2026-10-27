import pandas as pd
import joblib
from sklearn.preprocessing import MinMaxScaler

caminho_entrada = 'data/processed/dataset_limpo.csv'
caminho_saida = 'data/processed/dataset_normalizado.csv'
caminho_scaler = 'data/processed/scaler.pkl'

features_audio = [
    'tempo', 'loudness', 'valence', 'energy', 
    'danceability', 'speechiness', 'acousticness', 
    'instrumentalness', 'liveness'
]

print("A carregar o dataset limpo...")
df = pd.read_csv(caminho_entrada)

# Trata valores nulos apenas nas métricas de áudio
df[features_audio] = df[features_audio].fillna(0.0)

# Normaliza as colunas numéricas mantendo todas as outras intactas (incluindo track_genre)
scaler = MinMaxScaler()
df[features_audio] = scaler.fit_transform(df[features_audio])

df.to_csv(caminho_saida, index=False)
joblib.dump(scaler, caminho_scaler)

print(f"Dataset normalizado salvo com as colunas: {list(df.columns)}")