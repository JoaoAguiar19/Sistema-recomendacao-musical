import os
import numpy as np
import pandas as pd
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import pickle

from src.graph.graph import construir_grafo
from src.algoritmos.busca_astar import gerar_playlist_astar

app = FastAPI(title="Sistema de Recomendação Musical")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos de Requisição (Pydantic)
class RecomendacaoRequest(BaseModel):
    origem_id: str
    destino_id: str


# Variáveis globais em memória RAM
grafo_global = None
df_completo = None
matriz_nos_grafo = None
ids_nos_grafo = None
bpm_nos_grafo = None

FEATURES_AUDIO = [
    'tempo', 'valence', 'energy', 'danceability', 'loudness',
    'speechiness', 'acousticness', 'instrumentalness', 'liveness'
]


@app.on_event("startup")
def startup_event():
    global grafo_global, df_completo, matriz_nos_grafo, ids_nos_grafo, bpm_nos_grafo
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Define os caminhos corretos
    caminho_csv = os.path.join(BASE_DIR, 'data', 'processed', 'dataset_normalizado.csv')
    caminho_pkl = os.path.join(BASE_DIR, 'data', 'grafo_knn.pkl')
    
    print("A iniciar o servidor e a carregar o dataset completo para buscas...")
    colunas_necessarias = ['track_id', 'track_name', 'artists', 'popularity'] + FEATURES_AUDIO
    
    try:
        df_completo = pd.read_csv(caminho_csv, usecols=lambda c: c in colunas_necessarias)
        print(f"Dataset global carregado: {len(df_completo):,} músicas disponíveis para busca.")
    except Exception as e:
        print(f"Aviso: Não foi possível carregar o CSV completo ({e}). A busca on-demand será desativada.")
        df_completo = pd.DataFrame()

    if os.path.exists(caminho_pkl):
        print(f"A carregar grafo pré-computado do disco em: {caminho_pkl}")
        with open(caminho_pkl, 'rb') as f:
            grafo_global = pickle.load(f)
        print(f"Grafo carregado instantaneamente! Total de nós: {len(list(grafo_global.nodes))}")
    else:
        print("Arquivo de grafo pré-computado não encontrado. A gerar do zero...")
        grafo_global = construir_grafo(k_vizinhos=35, popularidade_minima=0)

    # Pré-computa matrizes NumPy dos nós do grafo para busca vetorial ultrarrápida
    ids_nos_grafo = list(grafo_global.nodes)
    matriz_nos_grafo = np.array([
        [float(grafo_global.nodes[nid].get(f, 0.0)) for f in FEATURES_AUDIO]
        for nid in ids_nos_grafo
    ])
    bpm_nos_grafo = np.array([
        float(grafo_global.nodes[nid].get('tempo', 0.0))
        for nid in ids_nos_grafo
    ])


def obter_dados_musica_dataset(track_id: str):
    """Busca os metadados completos de uma música no dataset global para exibir no frontend."""
    if df_completo is None or df_completo.empty:
        return None
    resultado = df_completo[df_completo['track_id'] == track_id]
    if resultado.empty:
        return None
    linha = resultado.iloc[0]
    return {
        "track_id": str(linha['track_id']),
        "nome": str(linha.get('track_name', 'Desconhecido')),
        "artista": str(linha.get('artists', 'Desconhecido')),
        "bpm": round(float(linha.get('tempo', 0)), 3)
    }


def encontrar_no_mais_proximo(track_id: str):
    """Encontra o nó do grafo mais parecido sonoramente usando cálculo vetorial (NumPy)."""
    if df_completo is None or df_completo.empty or matriz_nos_grafo is None:
        return None
        
    musica_alvo = df_completo[df_completo['track_id'] == track_id]
    if musica_alvo.empty:
        return None

    vetor_alvo = musica_alvo[FEATURES_AUDIO].fillna(0.0).values[0]
    bpm_alvo = float(musica_alvo['tempo'].values[0] if 'tempo' in musica_alvo else 0.0)

    # Distância Euclidiana vetorizada sobre todos os 25k nós em milissegundos
    distancias = np.linalg.norm(matriz_nos_grafo - vetor_alvo, axis=1)

    # Aplica penalização para diferenças de BPM acima de 15.0
    diferenca_bpm = np.abs(bpm_nos_grafo - bpm_alvo)
    penalizacao = np.where(diferenca_bpm > 15.0, 100.0, 0.0)
    distancias_finais = distancias + penalizacao

    idx_melhor = np.argmin(distancias_finais)
    return ids_nos_grafo[idx_melhor]


@app.get("/musicas")
def listar_musicas(
    limite: int = Query(default=15, ge=1, le=100),
    busca: Optional[str] = Query(default=None, description="Filtra por nome da música ou artista")
):
    if not grafo_global:
        raise HTTPException(status_code=500, detail="O grafo ainda não foi inicializado.")

    if not busca:
        resultado = []
        for track_id, dados in list(grafo_global.nodes(data=True))[:limite]:
            resultado.append({
                "track_id": track_id,
                "nome": str(dados.get("track_name", "")),
                "artista": str(dados.get("artists", "")),
                "bpm": round(float(dados.get("tempo", 0)), 3),
                "no_grafo": True
            })
        return {"musicas": resultado}

    termo = busca.lower()
    resultado = []
    ids_adicionados = set()
    nomes_vistos = set()

    # 1. Pesquisa primeiro no grafo K-NN (deduplicando por nome da música)
    for track_id, dados in grafo_global.nodes(data=True):
        nome = str(dados.get("track_name", ""))
        artista = str(dados.get("artists", ""))
        nome_chave = nome.lower().strip()

        if (termo in nome.lower() or termo in artista.lower()) and nome_chave not in nomes_vistos:
            resultado.append({
                "track_id": track_id,
                "nome": nome,
                "artista": artista,
                "bpm": round(float(dados.get("tempo", 0)), 3),
                "no_grafo": True
            })
            ids_adicionados.add(track_id)
            nomes_vistos.add(nome_chave)
            
            if len(resultado) >= limite:
                return {"musicas": resultado}

    # 2. Se faltarem resultados, pesquisa no dataset completo de 1.2M (ordenado por popularidade)
    if len(resultado) < limite and not df_completo.empty:
        mascara = (
            df_completo['track_name'].astype(str).str.lower().str.contains(termo, na=False) | 
            df_completo['artists'].astype(str).str.lower().str.contains(termo, na=False)
        )
        
        if 'popularity' in df_completo.columns:
            df_filtrado = df_completo[mascara].sort_values(by='popularity', ascending=False)
        else:
            df_filtrado = df_completo[mascara]
            
        df_filtrado = df_filtrado.drop_duplicates(subset=['track_name'], keep='first')

        for _, row in df_filtrado.iterrows():
            track_id = str(row['track_id'])
            nome = str(row.get('track_name', 'Desconhecido'))
            nome_chave = nome.lower().strip()

            if track_id not in ids_adicionados and nome_chave not in nomes_vistos:
                resultado.append({
                    "track_id": track_id,
                    "nome": nome,
                    "artista": str(row.get('artists', 'Desconhecido')),
                    "bpm": round(float(row.get('tempo', 0)), 3),
                    "no_grafo": False
                })
                ids_adicionados.add(track_id)
                nomes_vistos.add(nome_chave)

            if len(resultado) >= limite:
                break

    return {"musicas": resultado}


@app.post("/recomendar")
def recomendar_playlist(request: RecomendacaoRequest):
    if not grafo_global:
        raise HTTPException(status_code=500, detail="O grafo ainda não foi inicializado.")

    origem_original_id = request.origem_id
    destino_original_id = request.destino_id

    no_origem_grafo = origem_original_id
    no_destino_grafo = destino_original_id
    
    dados_musica_origem_extra = None
    dados_musica_destino_extra = None

    # Trata ORIGEM fora do grafo
    if origem_original_id not in grafo_global.nodes:
        dados_musica_origem_extra = obter_dados_musica_dataset(origem_original_id)
        no_origem_grafo = encontrar_no_mais_proximo(origem_original_id)
        if not no_origem_grafo:
            raise HTTPException(status_code=404, detail="Música inicial não encontrada no catálogo global.")

    # Trata DESTINO fora do grafo
    if destino_original_id not in grafo_global.nodes:
        dados_musica_destino_extra = obter_dados_musica_dataset(destino_original_id)
        no_destino_grafo = encontrar_no_mais_proximo(destino_original_id)
        if not no_destino_grafo:
            raise HTTPException(status_code=404, detail="Música final não encontrada no catálogo global.")
    
    # 1. Gera a rota A* através dos nós suportados pelo grafo
    playlist_ids = gerar_playlist_astar(grafo_global, no_origem_grafo, no_destino_grafo)
    
    if not playlist_ids:
        raise HTTPException(status_code=400, detail="Músicas incompatíveis ritmicamente. Não foi possível traçar uma rota contínua suave.")
    
    resultado = []
    
    # 2. Fixa a música original de origem no início (caso tenha vindo do dataset geral)
    if dados_musica_origem_extra:
        resultado.append(dados_musica_origem_extra)

    # 3. Adiciona o caminho gerado pelo A*
    for track_id in playlist_ids:
        dados_no = grafo_global.nodes[track_id]
        resultado.append({
            "track_id": track_id,
            "nome": str(dados_no.get("track_name", "Desconhecido")),
            "artista": str(dados_no.get("artists", "Desconhecido")),
            "bpm": round(float(dados_no.get("tempo", 0)), 3)
        })
        
    # 4. Fixa a música original de destino no fim (caso tenha vindo do dataset geral)
    if dados_musica_destino_extra:
        resultado.append(dados_musica_destino_extra)
        
    return {"playlist": resultado}