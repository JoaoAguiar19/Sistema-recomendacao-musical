import numpy as np
import networkx as nx


# Calcula a distância euclidiana entre os vetores de características de duas músicas.
def heuristica_euclidiana(u: str, v: str, G: nx.Graph) -> float:
    features_origem = G.nodes[u]['features']
    features_destino = G.nodes[v]['features'] 
    distancia = np.linalg.norm(features_origem - features_destino)
    return float(distancia)

# Executa o A* nativo do NetworkX e retorna o caminho e o custo total.
def buscar_caminho_astar(G: nx.Graph, inicio: str, destino: str) -> list[str]:
    caminho = nx.astar_path(
        G, 
        source=inicio, 
        target=destino, 
        heuristic=lambda u, v: heuristica_euclidiana(u, v, G), 
        weight='weight'
    )
    return caminho