import os
import pandas as pd

# Mapeamento dinâmico de caminhos para rodar de qualquer lugar
DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(DIRETORIO_ATUAL) 

caminho_bruto = os.path.join(BASE_DIR, 'data', 'raw', 'dataset.csv')
caminho_limpo = os.path.join(BASE_DIR, 'data', 'processed', 'dataset_limpo.csv')

print(f"A carregar dataset bruto de: {caminho_bruto}...")
df_bruto = pd.read_csv(caminho_bruto)

print("A padronizar o nome das colunas...")
mapeamento = {}
for col in df_bruto.columns:
    col_lower = col.lower()
    if col_lower in ['id', 'track_id', 'uri']:
        mapeamento[col] = 'track_id'
    elif col_lower in ['name', 'track_name', 'song', 'title']:
        mapeamento[col] = 'track_name'
    elif col_lower in ['artist', 'artists', 'artist_name']:
        mapeamento[col] = 'artists'

if mapeamento:
    df_bruto.rename(columns=mapeamento, inplace=True)

# Valores padrão caso o dataset não traga estes campos
if 'track_genre' not in df_bruto.columns:
    df_bruto['track_genre'] = 'Misto'

if 'popularity' not in df_bruto.columns:
    df_bruto['popularity'] = 50

# Colunas críticas exigidas pela aplicação
colunas_obrigatorias = ['track_id', 'track_name', 'artists', 'tempo', 'energy', 'danceability', 'duration_ms', 'track_genre']
colunas_existentes_obrigatorias = [col for col in colunas_obrigatorias if col in df_bruto.columns]

print("A aplicar limpeza, remoção de duplicatas e filtro de duração (1 a 10 minutos)...")
df_limpo = (
    df_bruto
    .drop(columns=['Unnamed: 0'], errors='ignore')
    # Filtro cirúrgico: remove vinhetas (< 1 min) e gravações excessivamente longas (> 10 min)
    .query("duration_ms >= 60000 and duration_ms <= 600000")
    .drop_duplicates(subset=['track_id'])
    .drop_duplicates(subset=['track_name', 'artists'])
    .dropna(subset=colunas_existentes_obrigatorias)
)

# Cria a pasta processed caso não exista
os.makedirs(os.path.dirname(caminho_limpo), exist_ok=True)

print("A guardar o dataset pré-processado...")
df_limpo.to_csv(caminho_limpo, index=False)

print(f"\n✅ Limpeza concluída! {len(df_limpo):,} de {len(df_bruto):,} registos válidos salvos.")
print(f"Salvo em: '{caminho_limpo}'.")