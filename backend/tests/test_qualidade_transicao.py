# test/test_qualidade_transicao.py
import sys
from pathlib import Path

# 1. Ajusta o caminho para reconhecer a pasta raiz do backend
RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

import numpy as np
import pandas as pd
from sqlalchemy import text
from core.database import engine
from src.graph.graph import construir_grafo_knn
from src.algoritmo.busca_a_star import buscar_caminho_astar

# Mapeamento da ordem das features gravadas no array NumPy
FEATURES_NOMES = [
    'tempo', 'loudness', 'valence', 'energy', 
    'danceability', 'speechiness', 'acousticness', 
    'instrumentalness', 'liveness'
]


def buscar_musicas_aleatorias():
    """Sorteia duas músicas do PostgreSQL para o teste."""
    query = text("""
        SELECT track_id, track_name, artists, track_genre 
        FROM musicas 
        ORDER BY RANDOM() 
        LIMIT 2;
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    
    return df.iloc[0], df.iloc[1]


def testar_qualidade_transicao():
    print("⏳ [1/3] Carregando 5050 músicas e construindo o Grafo K-NN...")
    G = construir_grafo_knn(k_neighbors=15)
    print(f"✅ Grafo montado: {G.number_of_nodes()} nós | {G.number_of_edges()} arestas.\n")

    print("🔎 [2/3] Sorteando músicas de Origem e Destino...")
    musica_a, musica_b = buscar_musicas_aleatorias()

    print(f"🟢 ORIGEM (A) : {musica_a['track_name']} — {musica_a['artists']}")
    print(f"🏁 DESTINO (B): {musica_b['track_name']} — {musica_b['artists']}\n")

    print("🚀 [3/3] Calculando caminho A* e analisando os atributos de áudio...")
    caminho = buscar_caminho_astar(G, inicio=musica_a['track_id'], destino=musica_b['track_id'])

    print(f"\n✨ ANÁLISE DETALHADA DA TRANSIÇÃO ({len(caminho)} MÚSICAS NO TOTAL):")
    print("=" * 85)

    custo_total = 0.0

    for i in range(len(caminho)):
        atual_id = caminho[i]
        node_atual = G.nodes[atual_id]
        feat = node_atual['features']

        nome = node_atual.get('track_name', 'Desconhecido')
        artista = node_atual.get('artists', 'Desconhecido')

        # Extração das características numéricas principais
        bpm = feat[0]
        loudness = feat[1]
        valence = feat[2]
        energy = feat[3]
        danceability = feat[4]
        acousticness = feat[6]

        if i == 0:
            tag = "🟢 [INÍCIO]"
            print(f"{tag} {nome} — {artista}")
            print(f"   📊 Atributos : BPM: {bpm:.1f} | Energy: {energy:.2f} | Danceability: {danceability:.2f} | Acousticness: {acousticness:.2f} | Valence: {valence:.2f}")
            print(f"   └── [Custo do Passo: 0.0000 | Custo Acumulado: 0.0000]")
        else:
            anterior_id = caminho[i - 1]
            feat_anterior = G.nodes[anterior_id]['features']

            # Peso da aresta no NetworkX
            if G.has_edge(anterior_id, atual_id):
                custo_passo = G[anterior_id][atual_id]['weight']
            else:
                custo_passo = float(np.linalg.norm(feat_anterior - feat))

            custo_total += custo_passo

            # Variação das métricas
            delta_bpm = bpm - feat_anterior[0]
            delta_energy = energy - feat_anterior[3]
            delta_dance = danceability - feat_anterior[4]

            tag = "🏁 [DESTINO]" if i == len(caminho) - 1 else f"🎵 [Passo {i}]"
            print(f"\n{tag} {nome} — {artista}")
            print(f"   📊 Atributos : BPM: {bpm:.1f} | Energy: {energy:.2f} | Danceability: {danceability:.2f} | Acousticness: {acousticness:.2f} | Valence: {valence:.2f}")
            print(f"   📐 Variação  : ΔBPM: {delta_bpm:+.1f} | ΔEnergy: {delta_energy:+.2f} | ΔDanceability: {delta_dance:+.2f}")
            print(f"   └── [Custo do Passo: {custo_passo:.4f} | Custo Acumulado: {custo_total:.4f}]")

    print("=" * 85)
    print(f"📈 CUSTO TOTAL RECOMENDADO DA PLAYLIST: {custo_total:.4f}")


if __name__ == "__main__":
    testar_qualidade_transicao()