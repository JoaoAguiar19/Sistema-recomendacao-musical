import math
import networkx as nx
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from core.database import engine

# Atributos numéricos de áudio utilizados no vetor de estilo
FEATURES_AUDIO = [
    'tempo', 'valence', 'energy', 'danceability', 'loudness',
    'speechiness', 'acousticness', 'instrumentalness', 'liveness'
]

GENEROS_ACEITOS = [
    'pop', 'rock', 'indie', 'alternative', 'latin', 'mpb', 'forro', 
    'sertanejo', 'dance', 'edm', 'r-n-b', 'country', 'soul', 'funk'
]


def _aplicar_filtros_musicas(df_musicas, popularidade_minima):
    if 'popularity' in df_musicas.columns:
        df_musicas = df_musicas[df_musicas['popularity'] >= popularidade_minima]

    coluna_genero = next(
        (nome for nome in ['track_genre', 'genre', 'genero'] if nome in df_musicas.columns), 
        None
    )
    if coluna_genero:
        df_musicas = df_musicas[df_musicas[coluna_genero].astype(str).str.lower().isin(GENEROS_ACEITOS)]

    if 'preview_url' in df_musicas.columns:
        df_musicas = df_musicas[df_musicas['preview_url'].notna() & (df_musicas['preview_url'] != '')]

    return df_musicas


def _inicializar_nos_grafo(df_musicas):
    grafo_musicas = nx.Graph()
    for _, linha in df_musicas.iterrows():
        grafo_musicas.add_node(linha['track_id'], **linha.to_dict())
    return grafo_musicas


def _conectar_vizinhos_knn(grafo_musicas, df_musicas, k_vizinhos):
    matriz_caracteristicas = df_musicas[FEATURES_AUDIO].fillna(0.0).values
    
    modelo_knn = NearestNeighbors(n_neighbors=k_vizinhos, metric='euclidean')
    modelo_knn.fit(matriz_caracteristicas)
    
    distancias, indices = modelo_knn.kneighbors(matriz_caracteristicas)
    ids_faixas = df_musicas['track_id'].tolist()

    for i, vizinhos in enumerate(indices):
        origem_id = ids_faixas[i]
        bpm_origem = float(df_musicas.iloc[i].get('tempo', 0.0) or 0.0)

        for j in range(1, len(vizinhos)):
            idx_destino = vizinhos[j]
            destino_id = ids_faixas[idx_destino]
            bpm_destino = float(df_musicas.iloc[idx_destino].get('tempo', 0.0) or 0.0)

            # Trava de Segurança
            if abs(bpm_origem - bpm_destino) > 0.08:
                continue

            custo_distancia = distancias[i][j]
            grafo_musicas.add_edge(origem_id, destino_id, weight=custo_distancia)


def construir_grafo(k_vizinhos=35, popularidade_minima=40):
    print("A carregar músicas da base de dados PostgreSQL...")
    df_musicas = pd.read_sql("SELECT * FROM musicas", engine)
    total_inicial = len(df_musicas)

    df_musicas = _aplicar_filtros_musicas(df_musicas, popularidade_minima)
    print(f"Filtragem concluída: {len(df_musicas)} de {total_inicial} faixas mantidas no grafo.")

    grafo_musicas = _inicializar_nos_grafo(df_musicas)
    
    print(f"A processar matriz KNN ({k_vizinhos} vizinhos por música)...")
    _conectar_vizinhos_knn(grafo_musicas, df_musicas, k_vizinhos)

    print(f"Grafo otimizado pronto: {grafo_musicas.number_of_nodes()} nós e {grafo_musicas.number_of_edges()} arestas.")
    return grafo_musicas