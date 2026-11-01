import networkx as nx
from src.algoritmos.custos_trajeto import calcular_peso_aresta
from src.algoritmos.heuristica_astar import heuristica_astar


def gerar_playlist_astar(grafo_musicas, origem_id, destino_id):
    if origem_id not in grafo_musicas or destino_id not in grafo_musicas:
        return None

    def peso_aresta_normalizado(musica_atual_id, musica_vizinha_id, atributos_aresta):
        return calcular_peso_aresta(
            grafo_musicas, musica_atual_id, musica_vizinha_id, 
            atributos_aresta
        )

    def fn_heuristica(musica_atual_id, musica_destino_id):
        return heuristica_astar(grafo_musicas, musica_atual_id, musica_destino_id)

    try:
        return nx.astar_path(
            G=grafo_musicas,
            source=origem_id,
            target=destino_id,
            heuristic=fn_heuristica,
            weight=peso_aresta_normalizado
        )
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None