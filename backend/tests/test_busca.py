# test/test_busca.py
import sys
from pathlib import Path

# 1. Identifica o diretório raiz 'backend'
RAIZ_PROJETO = Path(__file__).resolve().parent.parent

# 2. Adiciona o caminho do backend ao sys.path se ainda não estiver lá
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

# 3. Agora os seus imports funcionam perfeitamente!
import pandas as pd
from sqlalchemy import text
from core.database import engine
from src.graph.graph import construir_grafo_knn
from src.algoritmo.busca_a_star import buscar_caminho_astar


def buscar_musicas_aleatorias():
    """Busca 2 músicas aleatórias no PostgreSQL para testar."""
    query = text("""
        SELECT track_id, track_name, artists, track_genre 
        FROM musicas 
        ORDER BY RANDOM() 
        LIMIT 2;
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    
    return df.iloc[0], df.iloc[1]


def testar_algoritmo_a_star():
    print("⏳ [1/3] Carregando dados do PostgreSQL e gerando o Grafo...")
    G = construir_grafo_knn(k_neighbors=15)
    print(f"✅ Grafo montado com {G.number_of_nodes()} nós e {G.number_of_edges()} arestas!\n")

    print("🔎 [2/3] Sorteando 2 músicas da base para o teste...")
    musica_a, musica_b = buscar_musicas_aleatorias()

    print(f"🟢 ORIGEM (A) : {musica_a['track_name']} ({musica_a['artists']}) [{musica_a['track_genre']}]")
    print(f"🏁 DESTINO (B): {musica_b['track_name']} ({musica_b['artists']}) [{musica_b['track_genre']}]\n")

    print("🚀 [3/3] Executando a busca A*...")
    caminho = buscar_caminho_astar(G, inicio=musica_a['track_id'], destino=musica_b['track_id'])

    print(f"\n✨ CAMINHO GERADO COM SUCESSO! ({len(caminho)} músicas na playlist):\n")
    print("=" * 65)
    for i, track_id in enumerate(caminho, start=1):
        dados = G.nodes[track_id]
        nome = dados.get('track_name', 'Desconhecido')
        artista = dados.get('artists', 'Desconhecido')
        
        prefixo = "🟢 [INÍCIO] " if i == 1 else ("🏁 [DESTINO]" if i == len(caminho) else f"🎵 [Passo {i-1}]")
        print(f"{prefixo} {nome} — {artista}")
    print("=" * 65)


if __name__ == "__main__":
    testar_algoritmo_a_star()