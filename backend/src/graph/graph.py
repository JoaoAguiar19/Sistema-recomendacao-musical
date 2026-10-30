import math
import networkx as nx
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from core.database import engine
from src.algoritmos.metricas_audio import (
    MAX_DIFERENCA_ENERGIA,
    MAX_DIFERENCA_TEMPO,
)

# Atributos numéricos de áudio utilizados no vetor de estilo
FEATURES_AUDIO = [
    'tempo', 'valence', 'energy', 'danceability', 'loudness',
    'speechiness', 'acousticness', 'instrumentalness', 'liveness'
]


def _aplicar_filtros_musicas(df_musicas, popularidade_minima):
    # Se a coluna popularidade existir e tiver valores válidos reais, aplica de forma flexível, senão ignora
    if 'popularity' in df_musicas.columns and df_musicas['popularity'].max() > 1:
        df_musicas = df_musicas[df_musicas['popularity'] >= popularidade_minima]

    # Mantemos a verificação de preview URL apenas se ela realmente existir e for obrigatória para o player
    if 'preview_url' in df_musicas.columns:
        # Se quiseres garantir que só entram músicas com preview, podes filtrar, 
        # mas caso contrário, removemos para não perder faixas. Vamos manter opcional:
        pass

    return df_musicas


def _inicializar_nos_grafo(df_musicas):
    grafo_musicas = nx.Graph()
    for _, linha in df_musicas.iterrows():
        grafo_musicas.add_node(linha['track_id'], **linha.to_dict())
    return grafo_musicas


def _transicao_valida(musica_atual, musica_vizinha):
    tempo_atual = float(musica_atual.get('tempo', 0.0) or 0.0)
    tempo_vizinho = float(musica_vizinha.get('tempo', 0.0) or 0.0)
    energia_atual = float(musica_atual.get('energy', 0.0) or 0.0)
    energia_vizinha = float(musica_vizinha.get('energy', 0.0) or 0.0)
    diferenca_tempo = abs(tempo_atual - tempo_vizinho)
    diferenca_energia = abs(energia_atual - energia_vizinha)

    return (
        math.isfinite(tempo_atual)
        and math.isfinite(tempo_vizinho)
        and math.isfinite(energia_atual)
        and math.isfinite(energia_vizinha)
        and (
            diferenca_tempo <= MAX_DIFERENCA_TEMPO
            or math.isclose(diferenca_tempo, MAX_DIFERENCA_TEMPO)
        )
        and (
            diferenca_energia <= MAX_DIFERENCA_ENERGIA
            or math.isclose(diferenca_energia, MAX_DIFERENCA_ENERGIA)
        )
    )


def filtrar_transicoes_bruscas(grafo_musicas):
    arestas_invalidas = [
        (origem, destino)
        for origem, destino in grafo_musicas.edges
        if not _transicao_valida(
            grafo_musicas.nodes[origem], grafo_musicas.nodes[destino]
        )
    ]
    grafo_musicas.remove_edges_from(arestas_invalidas)
    return grafo_musicas


def _conectar_vizinhos_knn(grafo_musicas, df_musicas, k_vizinhos):
    matriz_caracteristicas = df_musicas[FEATURES_AUDIO].fillna(0.0).values
    
    modelo_knn = NearestNeighbors(n_neighbors=k_vizinhos, metric='euclidean')
    modelo_knn.fit(matriz_caracteristicas)
    
    distancias, indices = modelo_knn.kneighbors(matriz_caracteristicas)
    ids_faixas = df_musicas['track_id'].tolist()

    for i, vizinhos in enumerate(indices):
        origem_id = ids_faixas[i]
        musica_origem = df_musicas.iloc[i]

        for j in range(1, len(vizinhos)):
            idx_destino = vizinhos[j]
            destino_id = ids_faixas[idx_destino]
            musica_destino = df_musicas.iloc[idx_destino]

            if not _transicao_valida(musica_origem, musica_destino):
                continue

            custo_distancia = distancias[i][j]
            grafo_musicas.add_edge(origem_id, destino_id, weight=custo_distancia)

def construir_grafo(k_vizinhos=35, popularidade_minima=0):
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