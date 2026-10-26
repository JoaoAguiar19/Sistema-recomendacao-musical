import math
import networkx as nx
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from core.database import engine

FEATURES_AUDIO = [
    'tempo', 'valence', 'energy', 'danceability', 'loudness',
    'speechiness', 'acousticness', 'instrumentalness', 'liveness'
]

def distancia_euclidiana(attrs_node1, attrs_node2):
    soma_quadrados = 0
    for feature in FEATURES_AUDIO:
        val1 = float(attrs_node1.get(feature) or 0.0)
        val2 = float(attrs_node2.get(feature) or 0.0)
        soma_quadrados += (val1 - val2) ** 2
    return math.sqrt(soma_quadrados)

def construir_grafo(k_vizinhos=15):
    print("A carregar músicas da base de dados PostgreSQL...")
    df = pd.read_sql("SELECT * FROM musicas", engine)
    
    # Isola a matriz numérica para encontrar vizinhos próximos rapidamente
    X = df[FEATURES_AUDIO].fillna(0.0).values
    
    G = nx.Graph()
    print("A adicionar os nós (músicas)...")
    for _, row in df.iterrows():
        G.add_node(row['track_id'], **row.to_dict())
        
    print(f"A processar matriz KNN (limite de {k_vizinhos} conexões por música)...")
    knn = NearestNeighbors(n_neighbors=k_vizinhos, metric='euclidean')
    knn.fit(X)
    
    # Calcula as distâncias e os índices dos vizinhos mais próximos
    distancias, indices = knn.kneighbors(X)
    track_ids = df['track_id'].tolist()
    
    # Constrói as arestas restritas para evitar sobrecarga de memória
    for i, vizinhos in enumerate(indices):
        origem_id = track_ids[i]
        # j começa em 1 para ignorar a própria música (distância 0)
        for j in range(1, len(vizinhos)):
            destino_id = track_ids[vizinhos[j]]
            custo = distancias[i][j]
            G.add_edge(origem_id, destino_id, weight=custo)
            
    print(f"Grafo otimizado pronto: {G.number_of_nodes()} nós e {G.number_of_edges()} arestas.")
    return G

def heuristica_astar(u, v, G):
    return distancia_euclidiana(G.nodes[u], G.nodes[v])

def gerar_playlist_astar(G, origem_id, destino_id):
    try:
        caminho = nx.astar_path(
            G, 
            source=origem_id, 
            target=destino_id, 
            heuristic=lambda u, v: heuristica_astar(u, v, G),
            weight='weight'
        )
        return caminho
    except nx.NetworkXNoPath:
        return None
    except nx.NodeNotFound as e:
        print(f"Erro: nó não encontrado ({e})")
        return None

if __name__ == "__main__":
    grafo = construir_grafo(k_vizinhos=15)
    
    nos = list(grafo.nodes())
    if len(nos) >= 2:
        musica_origem = nos[0]
        musica_destino = nos[-1]
        
        nome_origem = grafo.nodes[musica_origem]['track_name']
        bpm_origem = float(grafo.nodes[musica_origem].get('tempo', 0))
        nome_destino = grafo.nodes[musica_destino]['track_name']
        bpm_destino = float(grafo.nodes[musica_destino].get('tempo', 0))
        
        print(f"\nA processar rota A* de '{nome_origem}' para '{nome_destino}'...")
        playlist = gerar_playlist_astar(grafo, musica_origem, musica_destino)
        
        if playlist:
            print(f"\nPlaylist gerada com {len(playlist)} faixas (A transição de BPM e features será gradual):")
            for i, track_id in enumerate(playlist):
                nome = grafo.nodes[track_id]['track_name']
                artista = grafo.nodes[track_id]['artists']
                bpm = float(grafo.nodes[track_id].get('tempo', 0))
                
                # Se o banco possuir dados passados pelo MinMaxScaler, o BPM aparecerá como decimal 0 a 1.
                print(f"{i+1}. {nome} - {artista} [Tempo/BPM: {bpm:.3f}]")
        else:
            print("Caminho não encontrado. Aumentar o 'k_vizinhos' ajuda a encontrar rotas mais difíceis.")