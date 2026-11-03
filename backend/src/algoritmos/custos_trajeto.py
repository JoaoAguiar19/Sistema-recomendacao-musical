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
    
    bpm_atual = float(node_atual.get('tempo', 0) or 0)
    bpm_vizinho = float(node_vizinho.get('tempo', 0) or 0)
    custo_bpm = calcular_custo_bpm(bpm_atual, bpm_vizinho)
    
    energia_atual = float(node_atual.get('energy', 0) or 0)
    energia_vizinha = float(node_vizinho.get('energy', 0) or 0)
    custo_energia = calcular_custo_energia(energia_atual, energia_vizinha)
    
    custo_harmonia = _calcular_custo_harmonia(node_atual, node_vizinho)
    custo_popularidade = _calcular_custo_popularidade(node_vizinho)

    custo_base = (
        (PESO_BPM * custo_bpm) +
        (PESO_ESTILO * custo_estilo) +
        (PESO_ENERGIA * custo_energia) +
        (PESO_HARMONIA * custo_harmonia) +
        (PESO_POPULARIDADE * custo_popularidade)
    )

    # --- PENALIZAÇÃO DE CHOQUE EXPANDIDA ---
    diferenca_bpm_real = abs(bpm_atual - bpm_vizinho)
    diferenca_energia_real = abs(energia_atual - energia_vizinha)
    diferenca_acustica = abs(float(node_atual.get('acousticness', 0) or 0) - float(node_vizinho.get('acousticness', 0) or 0))
    diferenca_valencia = abs(float(node_atual.get('valence', 0) or 0) - float(node_vizinho.get('valence', 0) or 0))
    
    fator_punicao = 1.0
    
    if diferenca_bpm_real > 0.04:
        fator_punicao += 20.0 * (diferenca_bpm_real / 0.04)
        
    if diferenca_energia_real > 0.3: 
        fator_punicao += 15.0 * (diferenca_energia_real / 0.3)
        
    # Impede saltos entre Pop Acústico e Metalcore (instrumentação pesada)
    if diferenca_acustica > 0.3:
        fator_punicao += 15.0 * (diferenca_acustica / 0.3)
        
    # Impede saltos de vibe (música feliz para música densa/agressiva)
    if diferenca_valencia > 0.3:
        fator_punicao += 10.0 * (diferenca_valencia / 0.3)

    return custo_base * fator_punicao