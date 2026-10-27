import pandas as pd

caminho_bruto = 'data/raw/dataset.csv'
caminho_limpo = 'data/processed/dataset_limpo.csv'

print("A carregar dataset bruto...")
df_bruto = pd.read_csv(caminho_bruto)

# Colunas críticas que não podem conter valores nulos para o funcionamento da aplicação
colunas_obrigatorias = ['track_id', 'track_name', 'artists', 'tempo', 'energy', 'danceability']
colunas_existentes_obrigatorias = [col for col in colunas_obrigatorias if col in df_bruto.columns]

print("A executar a limpeza de colunas e duplicatas...")
df_limpo = (
    df_bruto
    .drop(columns=['Unnamed: 0'], errors='ignore')
    .drop_duplicates(subset=['track_id'])
    .drop_duplicates(subset=['track_name', 'artists'])
    .dropna(subset=colunas_existentes_obrigatorias)
)

df_limpo.to_csv(caminho_limpo, index=False)

print(f"Limpeza concluída: {len(df_limpo)} de {len(df_bruto)} registros salvos em '{caminho_limpo}'.")
print(f"Colunas preservadas no dataset limpo: {list(df_limpo.columns)}")