import networkx as nx
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from core.database import engine

FEATURES_AUDIO = [
    'tempo', 'valence', 'energy', 'danceability', 'loudness',
    'speechiness', 'acousticness', 'instrumentalness', 'liveness'
]

def _aplicar_filtros_musicas(df_musicas, popularidade_minima):
    if 'popularity' in df_musicas.columns and df_musicas['popularity'].max() > 1:
        df_musicas = df_musicas[df_musicas['popularity'] >= popularidade_minima]
        
    # TRAVA DO PLAYER: Remove estritamente qualquer música que não tenha áudio de prévia
    if 'preview_url' in df_musicas.columns:
        df_musicas = df_musicas.dropna(subset=['preview_url'])
        # Garante que a string não está vazia
        df_musicas = df_musicas[df_musicas['preview_url'].astype(str).str.strip() != '']
        
    return df_musicas

def _inicializar_nos_grafo(df_musicas):
    grafo_musicas = nx.Graph()
    for _, linha in df_musicas.iterrows():
        grafo_musicas.add_node(linha['track_id'], **linha.to_dict())
    return grafo_musicas

def _conectar_vizinhos_knn(grafo_musicas, df_musicas, k_vizinhos):
    matriz_caracteristicas = df_musicas[FEATURES_AUDIO].fillna(0.0).values
    
    # CORREÇÃO: Mudar de k-vizinhos puros para um limite de RAIO.
    # O radius=0.3 garante que o algoritmo NUNCA liga duas músicas se a 
    # distância vetorial total entre elas for maior que 0.3, mesmo que 
    # não atinja os 60 vizinhos.
    modelo_knn = NearestNeighbors(radius=0.3, n_neighbors=k_vizinhos, metric='euclidean')
    modelo_knn.fit(matriz_caracteristicas)
    
    distancias, indices = modelo_knn.radius_neighbors(matriz_caracteristicas, sort_results=True)
    ids_faixas = df_musicas['track_id'].tolist()

    tempos = df_musicas['tempo'].fillna(0.0).to_numpy(dtype=float)
    energias = df_musicas['energy'].fillna(0.0).to_numpy(dtype=float)
    acusticas = df_musicas['acousticness'].fillna(0.0).to_numpy(dtype=float)
    valencias = df_musicas['valence'].fillna(0.0).to_numpy(dtype=float)

    for i, vizinhos in enumerate(indices):
        origem_id = ids_faixas[i]
        bpm_origem = tempos[i]
        energia_origem = energias[i]
        acustica_origem = acusticas[i]
        valencia_origem = valencias[i]

        for j_idx, vizinho_real_idx in enumerate(vizinhos):
            # Ignora a própria música (distância 0)
            if i == vizinho_real_idx:
                continue

            destino_id = ids_faixas[vizinho_real_idx]
            
            bpm_destino = tempos[vizinho_real_idx]
            energia_destino = energias[vizinho_real_idx]
            acustica_destino = acusticas[vizinho_real_idx]
            valencia_destino = valencias[vizinho_real_idx]

            # TRAVAS DE SEGURANÇA (Garante a transição gradual)
            if abs(bpm_origem - bpm_destino) > 0.06:
                continue
            if abs(energia_origem - energia_destino) > 0.20:
                continue
            if abs(acustica_origem - acustica_destino) > 0.25:
                continue
            if abs(valencia_origem - valencia_destino) > 0.25:
                continue

            custo_distancia = distancias[i][j_idx]
            grafo_musicas.add_edge(origem_id, destino_id, weight=custo_distancia)

# Aumentado os vizinhos de 35 para 60 para compensar as arestas que serão cortadas pelos filtros
def construir_grafo(k_vizinhos=60, popularidade_minima=0):
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