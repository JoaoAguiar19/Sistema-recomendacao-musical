import os
import pandas as pd
import joblib
from sklearn.preprocessing import MinMaxScaler

# Mapeamento dinâmico de caminhos para rodar de qualquer lugar
DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(DIRETORIO_ATUAL) 

caminho_entrada = os.path.join(BASE_DIR, 'data', 'processed', 'dataset_limpo.csv')
caminho_saida = os.path.join(BASE_DIR, 'data', 'processed', 'dataset_normalizado.csv')
caminho_scaler = os.path.join(BASE_DIR, 'data', 'processed', 'scaler.pkl')

features_audio_desejadas = [
    'tempo', 'loudness', 'valence', 'energy', 
    'danceability', 'speechiness', 'acousticness', 
    'instrumentalness', 'liveness'
]

print("A carregar o dataset limpo...")
df = pd.read_csv(caminho_entrada)

# Garante que só tentamos normalizar as colunas que realmente vieram no dataset do Kaggle
features_existentes = [col for col in features_audio_desejadas if col in df.columns]

print(f"Métricas encontradas para normalização: {features_existentes}")

# Trata valores nulos apenas nas métricas de áudio
df[features_existentes] = df[features_existentes].fillna(0.0)

# Normaliza as colunas numéricas (escala de 0 a 1) mantendo as de texto intactas
scaler = MinMaxScaler()
df[features_existentes] = scaler.fit_transform(df[features_existentes])

print("A guardar o dataset normalizado e o modelo scaler...")
df.to_csv(caminho_saida, index=False)
joblib.dump(scaler, caminho_scaler)

print(f"✅ Sucesso! Dataset normalizado ({len(df):,} faixas) salvo em: {caminho_saida}")