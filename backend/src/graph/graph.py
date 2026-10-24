import networkx as nx
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from core.database import engine

FEATURES = [
    'tempo', 'loudness', 'valence', 'energy', 
    'danceability', 'speechiness', 'acousticness', 
    'instrumentalness', 'liveness'
]


def carregar_dados() -> pd.DataFrame:
    query = f"""
    SELECT track_id, track_name, artists, track_genre, {', '.join(FEATURES)} 
    FROM musicas
    """
    df = pd.read_sql(query, con=engine)
    
    if df.empty:
        raise ValueError("A tabela 'musicas' está vazia!")
        
    return df


def calcular_knn(df: pd.DataFrame, k_neighbors: int):
    knn = NearestNeighbors(n_neighbors=k_neighbors, metric='euclidean')
    knn.fit(df[FEATURES])
    distances, indices = knn.kneighbors(df[FEATURES])
    return distances, indices

# Insere as músicas como nós do grafo com o vetor de características otimizado.

def adicionar_nos(G: nx.Graph, df: pd.DataFrame) -> None:
    for _, row in df.iterrows():
        G.add_node(
            row['track_id'], 
            track_name=row['track_name'],
            artists=row['artists'],
            features=row[FEATURES].to_numpy(dtype=float)
        )

# Cria as conexões (arestas) entre as músicas vizinhas com peso de distância euclidiana.

def adicionar_arestas(G: nx.Graph, df: pd.DataFrame, distances, indices, k_neighbors: int) -> None:
    for i in range(len(df)):
        source_id = df.iloc[i]['track_id']
        for j in range(1, k_neighbors):
            target_id = df.iloc[indices[i][j]]['track_id']
            G.add_edge(source_id, target_id, weight=float(distances[i][j]))

# Orquestra a criação do grafo de músicas.
def criar_grafo(df: pd.DataFrame, distances, indices, k_neighbors: int) -> nx.Graph:
    G = nx.Graph()
    adicionar_nos(G, df)
    adicionar_arestas(G, df, distances, indices, k_neighbors)
    return G


# Função principal para carregar dados, calcular vizinhos e retornar o grafo montado.

def construir_grafo_knn(k_neighbors: int = 15) -> nx.Graph:
    df = carregar_dados()
    distances, indices = calcular_knn(df, k_neighbors)
    return criar_grafo(df, distances, indices, k_neighbors)