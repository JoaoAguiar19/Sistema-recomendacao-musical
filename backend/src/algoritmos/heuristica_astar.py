import math
from src.algoritmos.metricas_audio import PESO_ESTILO, PESO_BPM

FEATURES_AUDIO = [
    'tempo', 'valence', 'energy', 'danceability', 'loudness',
    'speechiness', 'acousticness', 'instrumentalness', 'liveness'
]

def heuristica_astar(grafo_musicas, musica_atual_id, musica_destino_id):
    node_atual = grafo_musicas.nodes[musica_atual_id]
    node_destino = grafo_musicas.nodes[musica_destino_id]
    
    distancia_quadrada = 0.0
    for feature in FEATURES_AUDIO:
        val_atual = float(node_atual.get(feature, 0.0) or 0.0)
        val_destino = float(node_destino.get(feature, 0.0) or 0.0)
        distancia_quadrada += (val_atual - val_destino) ** 2
        
    # Combina a precisão matemática total com o peso base do projeto
    return math.sqrt(distancia_quadrada) * ((PESO_ESTILO + PESO_BPM) / 2.0)