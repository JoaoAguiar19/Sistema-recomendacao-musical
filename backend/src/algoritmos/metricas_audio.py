import math

# Pesos da Função de Custo Unificada (A soma dos pesos é igual a 1.0)
PESO_BPM = 0.35      
PESO_ESTILO = 0.10      
PESO_ENERGIA = 0.30
PESO_HARMONIA = 0.25     
PESO_POPULARIDADE = 0.05 

FEATURES_AUDIO = [
    'tempo', 'valence', 'energy', 'danceability', 'loudness',
    'speechiness', 'acousticness', 'instrumentalness', 'liveness'
]

MAX_DIFERENCA_TEMPO = 0.08
MAX_DIFERENCA_ENERGIA = 0.15


def distancia_euclidiana(atributos_musica_1, atributos_musica_2):
    soma_quadrados = 0
    for feature in FEATURES_AUDIO:
        valor_feature_1 = float(atributos_musica_1.get(feature) or 0.0)
        valor_feature_2 = float(atributos_musica_2.get(feature) or 0.0)
        soma_quadrados += (valor_feature_1 - valor_feature_2) ** 2
    return math.sqrt(soma_quadrados)


def distancia_ciclo_quintas_normalizada(tom_musica_1, modo_musica_1, tom_musica_2, modo_musica_2):
    posicao_ciclo_1 = (int(tom_musica_1) * 7) % 12
    posicao_ciclo_2 = (int(tom_musica_2) * 7) % 12
    distancia_notas = abs(posicao_ciclo_1 - posicao_ciclo_2)
    distancia_circulo = min(distancia_notas, 12 - distancia_notas)
    penalidade_modo = 0.5 if modo_musica_1 != modo_musica_2 else 0.0
    return min(1.0, (distancia_circulo + penalidade_modo) / 6.5)


def calcular_custo_bpm(bpm_atual, bpm_vizinho):
    salto_bpm = abs(bpm_vizinho - bpm_atual)
    return min(1.0, (salto_bpm / MAX_DIFERENCA_TEMPO) ** 2)


def calcular_custo_energia(energia_atual, energia_vizinha):
    salto_energia = abs(energia_vizinha - energia_atual)
    return min(1.0, salto_energia / MAX_DIFERENCA_ENERGIA)