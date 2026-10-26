import math
import networkx as nx
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from core.database import engine

# Atributos numéricos de áudio utilizados no vetor de estilo
FEATURES_AUDIO = [
    'tempo', 'valence', 'energy', 'danceability', 'loudness',
    'speechiness', 'acousticness', 'instrumentalness', 'liveness'
]

# Pesos da Função de Custo Unificada (A soma dos pesos é igual a 1.0)
PESO_BPM = 0.40          # Prioridade reforçada na progressão contínua de velocidade
PESO_ESTILO = 0.20       # Proximidade tímbrica e rítmica geral (vetor de áudio)
PESO_ENERGIA = 0.15      # Progressão contínua de intensidade sonora
PESO_HARMONIA = 0.15     # Compatibilidade tonal (Ciclo das Quintas)
PESO_POPULARIDADE = 0.10 # Preferência por faixas famosas e conhecidas

GENEROS_ACEITOS = [
    'pop', 'rock', 'indie', 'alternative', 'latin', 'mpb', 'forro', 
    'sertanejo', 'dance', 'edm', 'r-n-b', 'country', 'soul', 'funk'
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


def construir_grafo(k_vizinhos=35, popularidade_minima=40):
    print("A carregar músicas da base de dados PostgreSQL...")
    df_musicas = pd.read_sql("SELECT * FROM musicas", engine)

    total_inicial = len(df_musicas)

    # 1. Filtro por Popularidade Mínima
    if 'popularity' in df_musicas.columns:
        df_musicas = df_musicas[df_musicas['popularity'] >= popularidade_minima]

    # 2. Filtragem por gênero musical
    coluna_genero = None
    for possivel_nome in ['track_genre', 'genre', 'genero']:
        if possivel_nome in df_musicas.columns:
            coluna_genero = possivel_nome
            break

    if coluna_genero:
        df_musicas = df_musicas[df_musicas[coluna_genero].astype(str).str.lower().isin(GENEROS_ACEITOS)]

    # 3. Filtro por prévia de áudio
    if 'preview_url' in df_musicas.columns:
        df_musicas = df_musicas[df_musicas['preview_url'].notna() & (df_musicas['preview_url'] != '')]

    print(f"Filtragem concluída: {len(df_musicas)} de {total_inicial} faixas mantidas no grafo.")

    matriz_caracteristicas = df_musicas[FEATURES_AUDIO].fillna(0.0).values

    grafo_musicas = nx.Graph()
    for _, linha in df_musicas.iterrows():
        grafo_musicas.add_node(linha['track_id'], **linha.to_dict())

    print(f"A processar matriz KNN ({k_vizinhos} vizinhos por música)...")
    modelo_knn = NearestNeighbors(n_neighbors=k_vizinhos, metric='euclidean')
    modelo_knn.fit(matriz_caracteristicas)

    distancias, indices = modelo_knn.kneighbors(matriz_caracteristicas)
    ids_faixas = df_musicas['track_id'].tolist()

    for i, vizinhos in enumerate(indices):
        origem_id = ids_faixas[i]
        bpm_origem = float(df_musicas.iloc[i].get('tempo', 0.0) or 0.0)

        for j in range(1, len(vizinhos)):
            idx_destino = vizinhos[j]
            destino_id = ids_faixas[idx_destino]
            bpm_destino = float(df_musicas.iloc[idx_destino].get('tempo', 0.0) or 0.0)

            # Trava de Segurança: Descarta arestas com variação bruta de BPM superior a 0.08 na escala [0, 1]
            if abs(bpm_origem - bpm_destino) > 0.08:
                continue

            custo_distancia = distancias[i][j]
            grafo_musicas.add_edge(origem_id, destino_id, weight=custo_distancia)

    print(f"Grafo otimizado pronto: {grafo_musicas.number_of_nodes()} nós e {grafo_musicas.number_of_edges()} arestas.")
    return grafo_musicas


def gerar_playlist_astar(grafo_musicas, origem_id, destino_id):
    if origem_id not in grafo_musicas or destino_id not in grafo_musicas:
        return None

    bpm_origem = float(grafo_musicas.nodes[origem_id].get('tempo', 0) or 0)
    bpm_destino = float(grafo_musicas.nodes[destino_id].get('tempo', 0) or 0)
    subindo_bpm = bpm_destino >= bpm_origem

    energia_origem = float(grafo_musicas.nodes[origem_id].get('energy', 0) or 0)
    energia_destino = float(grafo_musicas.nodes[destino_id].get('energy', 0) or 0)
    subindo_energia = energia_destino >= energia_origem

    def peso_aresta_normalizado(musica_atual_id, musica_vizinha_id, atributos_aresta):
        # 1. Custo de Estilo / Timbre
        distancia_bruta = atributos_aresta.get('weight', 1.0)
        custo_estilo = min(1.0, distancia_bruta / 2.0)

        # 2. Custo de Variação de BPM em escala [0.0, 1.0]
        bpm_atual = float(grafo_musicas.nodes[musica_atual_id].get('tempo', 0) or 0)
        bpm_vizinho = float(grafo_musicas.nodes[musica_vizinha_id].get('tempo', 0) or 0)
        delta_bpm = bpm_vizinho - bpm_atual

        if subindo_bpm and delta_bpm < 0:
            custo_bpm = 1.0  # Penalidade máxima por contrariar a tendência
        elif not subindo_bpm and delta_bpm > 0:
            custo_bpm = 1.0  # Penalidade máxima por contrariar a tendência
        else:
            salto_bpm = abs(delta_bpm)
            # Escala ajustada: variações até 0.08 sobem quadraticamente; acima de 0.08 penalizam no limite
            custo_bpm = min(1.0, (salto_bpm / 0.08) ** 2)

        # 3. Custo de Variação de Energia
        energia_atual = float(grafo_musicas.nodes[musica_atual_id].get('energy', 0) or 0)
        energia_vizinha = float(grafo_musicas.nodes[musica_vizinha_id].get('energy', 0) or 0)
        delta_energia = energia_vizinha - energia_atual

        if subindo_energia and delta_energia < 0:
            custo_energia = 1.0
        elif not subindo_energia and delta_energia > 0:
            custo_energia = 1.0
        else:
            salto_energia = abs(delta_energia)
            custo_energia = min(1.0, salto_energia / 0.15)

        # 4. Custo Harmônico Tonal
        tom_atual = grafo_musicas.nodes[musica_atual_id].get('key', 0) or 0
        modo_atual = grafo_musicas.nodes[musica_atual_id].get('mode', 1) or 1
        tom_vizinho = grafo_musicas.nodes[musica_vizinha_id].get('key', 0) or 0
        modo_vizinho = grafo_musicas.nodes[musica_vizinha_id].get('mode', 1) or 1

        custo_harmonia = distancia_ciclo_quintas_normalizada(tom_atual, modo_atual, tom_vizinho, modo_vizinho)

        # 5. Custo de Popularidade
        popularidade_vizinha = float(grafo_musicas.nodes[musica_vizinha_id].get('popularity', 50) or 50)
        custo_popularidade = 1.0 - (popularidade_vizinha / 100.0)

        return (
            (PESO_BPM * custo_bpm) +
            (PESO_ESTILO * custo_estilo) +
            (PESO_ENERGIA * custo_energia) +
            (PESO_HARMONIA * custo_harmonia) +
            (PESO_POPULARIDADE * custo_popularidade)
        )

    def heuristica_astar(musica_atual_id, musica_destino_id):
        distancia_estilo = distancia_euclidiana(
            grafo_musicas.nodes[musica_atual_id], 
            grafo_musicas.nodes[musica_destino_id]
        ) / 2.0

        bpm_atual = float(grafo_musicas.nodes[musica_atual_id].get('tempo', 0) or 0)
        bpm_destino = float(grafo_musicas.nodes[musica_destino_id].get('tempo', 0) or 0)
        distancia_bpm = min(1.0, abs(bpm_atual - bpm_destino) / 0.5)

        return (distancia_estilo * PESO_ESTILO) + (distancia_bpm * PESO_BPM)

    try:
        caminho_playlist = nx.astar_path(
            G=grafo_musicas,
            source=origem_id,
            target=destino_id,
            heuristic=heuristica_astar,
            weight=peso_aresta_normalizado
        )
        return caminho_playlist
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None