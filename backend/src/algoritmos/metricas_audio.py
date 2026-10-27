import math

# Pesos da Função de Custo Unificada (A soma dos pesos é igual a 1.0)
PESO_BPM = 0.40          
PESO_ESTILO = 0.20       
PESO_ENERGIA = 0.15      
PESO_HARMONIA = 0.15     
PESO_POPULARIDADE = 0.10 

FEATURES_AUDIO = [
    'tempo', 'valence', 'energy', 'danceability', 'loudness',
    'speechiness', 'acousticness', 'instrumentalness', 'liveness'
]


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


def calcular_custo_bpm(bpm_atual, bpm_vizinho, subindo_bpm):
    delta_bpm = bpm_vizinho - bpm_atual
    if (subindo_bpm and delta_bpm < 0) or (not subindo_bpm and delta_bpm > 0):
        return 1.0
    
    salto_bpm = abs(delta_bpm)
    return min(1.0, (salto_bpm / 0.08) ** 2)


def calcular_custo_energia(energia_atual, energia_vizinha, subindo_energia):
    delta_energia = energia_vizinha - energia_atual
    if (subindo_energia and delta_energia < 0) or (not subindo_energia and delta_energia > 0):
        return 1.0
    
    salto_energia = abs(delta_energia)
    return min(1.0, salto_energia / 0.15)