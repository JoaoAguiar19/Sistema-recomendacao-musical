from src.algoritmos.metricas_audio import PESO_BPM, PESO_ESTILO, distancia_euclidiana


def heuristica_astar(grafo_musicas, musica_atual_id, musica_destino_id):
    node_atual = grafo_musicas.nodes[musica_atual_id]
    node_destino = grafo_musicas.nodes[musica_destino_id]

    distancia_estilo = distancia_euclidiana(node_atual, node_destino) / 2.0

    bpm_atual = float(node_atual.get('tempo', 0) or 0)
    bpm_destino = float(node_destino.get('tempo', 0) or 0)
    distancia_bpm = min(1.0, abs(bpm_atual - bpm_destino) / 0.5)

    return (distancia_estilo * PESO_ESTILO) + (distancia_bpm * PESO_BPM)