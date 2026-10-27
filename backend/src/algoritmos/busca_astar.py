import networkx as nx
from src.algoritmos.custos_trajeto import calcular_peso_aresta
from src.algoritmos.heuristica_astar import heuristica_astar


def _obter_tendencias_trajeto(grafo_musicas, origem_id, destino_id):
    bpm_origem = float(grafo_musicas.nodes[origem_id].get('tempo', 0) or 0)
    bpm_destino = float(grafo_musicas.nodes[destino_id].get('tempo', 0) or 0)
    
    energia_origem = float(grafo_musicas.nodes[origem_id].get('energy', 0) or 0)
    energia_destino = float(grafo_musicas.nodes[destino_id].get('energy', 0) or 0)

    return bpm_destino >= bpm_origem, energia_destino >= energia_origem


def gerar_playlist_astar(grafo_musicas, origem_id, destino_id):
    if origem_id not in grafo_musicas or destino_id not in grafo_musicas:
        return None

    subindo_bpm, subindo_energia = _obter_tendencias_trajeto(grafo_musicas, origem_id, destino_id)

    def peso_aresta_normalizado(musica_atual_id, musica_vizinha_id, atributos_aresta):
        return calcular_peso_aresta(
            grafo_musicas, musica_atual_id, musica_vizinha_id, 
            atributos_aresta, subindo_bpm, subindo_energia
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