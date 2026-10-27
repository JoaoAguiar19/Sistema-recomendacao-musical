import pandas as pd

caminho_bruto = 'data/raw/dataset.csv'
caminho_limpo = 'data/processed/dataset_limpo.csv'

df_bruto = pd.read_csv(caminho_bruto)
df_limpo = pd.read_csv(caminho_limpo)

print("=== RELATÓRIO DE VALIDAÇÃO DO DATASET ===")
print(f"Linhas originais: {len(df_bruto)}")
print(f"Linhas após limpeza: {len(df_limpo)}")
print(f"Linhas removidas: {len(df_bruto) - len(df_limpo)}\n")

duplicatas_id = df_limpo.duplicated(subset=['track_id']).sum()
duplicatas_nome_artista = df_limpo.duplicated(subset=['track_name', 'artists']).sum()

features_audio = [
    'tempo', 'valence', 'energy', 'danceability', 'loudness', 
    'speechiness', 'acousticness', 'instrumentalness', 'liveness'
]
features_presentes = [f for f in features_audio if f in df_limpo.columns]
nulos_features = df_limpo[features_presentes].isnull().sum().sum()

metadados_contexto = ['popularity', 'track_genre', 'key', 'mode', 'preview_url']
metadados_encontrados = [col for col in metadados_contexto if col in df_limpo.columns]
metadados_ausentes = [col for col in metadados_contexto if col not in df_limpo.columns]

print(f"Duplicatas de ID (track_id): {duplicatas_id}")
print(f"Duplicatas de Faixa (track_name + artists): {duplicatas_nome_artista}")
print(f"Valores nulos nas features de áudio: {nulos_features}")
print(f"Metadados de contexto validados: {metadados_encontrados}")

if metadados_ausentes:
    print(f"AVISO: As seguintes colunas de contexto NÃO estão presentes no CSV: {metadados_ausentes}")

if duplicatas_id == 0 and duplicatas_nome_artista == 0 and nulos_features == 0 and not metadados_ausentes:
    print("\nDataset aprovado com sucesso. Pronto para a etapa de normalização.")
else:
    print("\nAtenção: Verifique os avisos acima antes de prosseguir com a inserção no banco.")