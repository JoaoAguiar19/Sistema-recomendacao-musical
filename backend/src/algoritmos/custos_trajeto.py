from src.algoritmos.metricas_audio import (
    PESO_BPM, PESO_ESTILO, PESO_ENERGIA, PESO_HARMONIA, PESO_POPULARIDADE,
    distancia_ciclo_quintas_normalizada, calcular_custo_bpm, calcular_custo_energia
)


def _calcular_custo_harmonia(node_atual, node_vizinho):
    return distancia_ciclo_quintas_normalizada(
        node_atual.get('key', 0) or 0, node_atual.get('mode', 1) or 1,
        node_vizinho.get('key', 0) or 0, node_vizinho.get('mode', 1) or 1
    )


def _calcular_custo_popularidade(node_vizinho):
    popularidade = node_vizinho.get('popularity')
    popularidade_vizinha = 50.0 if popularidade is None else float(popularidade)
    return 1.0 - (min(100.0, max(0.0, popularidade_vizinha)) / 100.0)


def calcular_peso_aresta(grafo_musicas, musica_atual_id, musica_vizinha_id, atributos_aresta):
    node_atual = grafo_musicas.nodes[musica_atual_id]
    node_vizinho = grafo_musicas.nodes[musica_vizinha_id]

    custo_estilo = min(1.0, max(0.0, float(atributos_aresta.get('weight', 1.0))) / 2.0)
    
    custo_bpm = calcular_custo_bpm(
        float(node_atual.get('tempo', 0) or 0),
        float(node_vizinho.get('tempo', 0) or 0)
    )
    
    custo_energia = calcular_custo_energia(
        float(node_atual.get('energy', 0) or 0),
        float(node_vizinho.get('energy', 0) or 0)
    )
    
    custo_harmonia = _calcular_custo_harmonia(node_atual, node_vizinho)
    custo_popularidade = _calcular_custo_popularidade(node_vizinho)

    return (
        (PESO_BPM * custo_bpm) +
        (PESO_ESTILO * custo_estilo) +
        (PESO_ENERGIA * custo_energia) +
        (PESO_HARMONIA * custo_harmonia) +
        (PESO_POPULARIDADE * custo_popularidade)
    )