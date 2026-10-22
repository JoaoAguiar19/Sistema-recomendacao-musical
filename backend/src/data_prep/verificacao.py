import pandas as pd

raw = pd.read_csv('data/raw/dataset.csv')
clean = pd.read_csv('data/processed/dataset_limpo.csv')

print(f"Linhas originais: {len(raw)}")
print(f"Linhas após limpeza: {len(clean)}")
print(f"Removidas: {len(raw) - len(clean)}\n")

duplicatas = clean.duplicated(subset=['track_id']).sum()
nulos = clean[['tempo', 'valence', 'energy', 'danceability']].isnull().sum().sum()

print(f"Duplicatas (track_id): {duplicatas}")
print(f"Valores NaN nas features: {nulos}")

if duplicatas == 0 and nulos == 0:
    print("\nDataset validado.")
else:
    print("\nFalha na validação: checar pipeline de limpeza.")