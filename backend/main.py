import os
import numpy as np
import pandas as pd
import networkx as nx
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import pickle

from src.graph.graph import construir_grafo, filtrar_transicoes_bruscas
from src.algoritmos.busca_astar import gerar_playlist_astar
from src.algoritmos.perfis_percurso import (
    PERFIS_PERCURSO,
    obter_perfil,
    serializar_perfil,
)
from src.algoritmos.metricas_audio import (
    MAX_DIFERENCA_ENERGIA,
    MAX_DIFERENCA_TEMPO,
)

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


class RecomendacaoPerfilRequest(BaseModel):
    percurso_id: str


# Variáveis globais em memória RAM
grafo_global = None
df_completo = None
matriz_nos_grafo = None
ids_nos_grafo = None
bpm_nos_grafo = None
energia_nos_grafo = None
nos_componente_principal = set()

FEATURES_AUDIO = [
    'tempo', 'valence', 'energy', 'danceability', 'loudness',
    'speechiness', 'acousticness', 'instrumentalness', 'liveness'
]


@app.on_event("startup")
def startup_event():
    global grafo_global, df_completo, matriz_nos_grafo, ids_nos_grafo
    global bpm_nos_grafo, energia_nos_grafo, nos_componente_principal
    
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

    arestas_antes_filtro = grafo_global.number_of_edges()
    filtrar_transicoes_bruscas(grafo_global)
    arestas_removidas = arestas_antes_filtro - grafo_global.number_of_edges()
    if arestas_removidas:
        print(f"Transições com saltos bruscos removidas: {arestas_removidas:,}.")
    nos_componente_principal = max(
        nx.connected_components(grafo_global), key=len, default=set()
    )

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
    energia_nos_grafo = np.array([
        float(grafo_global.nodes[nid].get('energy', 0.0))
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
    if (
        df_completo is None
        or df_completo.empty
        or matriz_nos_grafo is None
        or bpm_nos_grafo is None
        or energia_nos_grafo is None
        or not nos_componente_principal
    ):
        return None
        
    musica_alvo = df_completo[df_completo['track_id'] == track_id]
    if musica_alvo.empty:
        return None

    vetor_alvo = musica_alvo[FEATURES_AUDIO].fillna(0.0).values[0]
    bpm_alvo = float(musica_alvo['tempo'].values[0] if 'tempo' in musica_alvo else 0.0)

    # As características do dataset e do grafo estão normalizadas.
    distancias = np.linalg.norm(matriz_nos_grafo - vetor_alvo, axis=1)

    diferenca_bpm = np.abs(bpm_nos_grafo - bpm_alvo)
    energia_alvo = float(musica_alvo['energy'].values[0])
    diferenca_energia = np.abs(energia_nos_grafo - energia_alvo)
    nos_componentes_validos = np.isin(ids_nos_grafo, list(nos_componente_principal))
    candidatos_validos = (
        (diferenca_bpm <= MAX_DIFERENCA_TEMPO)
        & (diferenca_energia <= MAX_DIFERENCA_ENERGIA)
        & nos_componentes_validos
    )
    distancias_finais = np.where(candidatos_validos, distancias, np.inf)

    idx_melhor = np.argmin(distancias_finais)
    if not np.isfinite(distancias_finais[idx_melhor]):
        return None
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


@app.get("/percursos")
def listar_percursos():
    return {"percursos": [serializar_perfil(perfil) for perfil in PERFIS_PERCURSO]}


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
            raise HTTPException(
                status_code=404,
                detail="Não foi encontrada uma faixa próxima com BPM e energia compatíveis para a música inicial.",
            )

    # Trata DESTINO fora do grafo
    if destino_original_id not in grafo_global.nodes:
        dados_musica_destino_extra = obter_dados_musica_dataset(destino_original_id)
        no_destino_grafo = encontrar_no_mais_proximo(destino_original_id)
        if not no_destino_grafo:
            raise HTTPException(
                status_code=404,
                detail="Não foi encontrada uma faixa próxima com BPM e energia compatíveis para a música final.",
            )
    
    # 1. Gera a rota A* através dos nós suportados pelo grafo
    playlist_ids = gerar_playlist_astar(grafo_global, no_origem_grafo, no_destino_grafo)
    
    if not playlist_ids:
        raise HTTPException(
            status_code=400,
            detail="Não foi possível traçar uma rota com transições compatíveis de BPM e energia entre essas músicas.",
        )
    
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


@app.post("/recomendar-percurso")
def recomendar_percurso_predefinido(request: RecomendacaoPerfilRequest):
    if not grafo_global:
        raise HTTPException(status_code=500, detail="O grafo ainda não foi inicializado.")

    perfil = obter_perfil(request.percurso_id)
    if perfil is None:
        raise HTTPException(status_code=404, detail="Percurso predefinido não encontrado.")

    bpm_inicial = perfil["bpm_inicial"]
    bpm_final = perfil["bpm_final"]

    def obter_candidatos(intervalo_bpm):
        candidatos = []

        for track_id, dados in grafo_global.nodes(data=True):
            tempo = float(dados.get("tempo", 0.0) or 0.0)
            if (
                track_id in nos_componente_principal
                and intervalo_bpm["min"] <= tempo <= intervalo_bpm["max"]
            ):
                candidatos.append(track_id)
        return candidatos

    candidatos_origem = obter_candidatos(bpm_inicial)
    candidatos_destino = obter_candidatos(bpm_final)
    if not candidatos_origem or not candidatos_destino:
        raise HTTPException(
            status_code=404,
            detail="Não há músicas suficientes no catálogo para as faixas de BPM deste percurso.",
        )

    gerador_aleatorio = np.random.default_rng()
    origem_id = gerador_aleatorio.choice(candidatos_origem)
    destinos_diferentes = [
        track_id for track_id in candidatos_destino if track_id != origem_id
    ]
    if not destinos_diferentes:
        raise HTTPException(
            status_code=404,
            detail="Não há duas músicas diferentes dentro dos intervalos de BPM deste percurso.",
        )
    destino_id = gerador_aleatorio.choice(destinos_diferentes)
    playlist_ids = gerar_playlist_astar(grafo_global, origem_id, destino_id)

    if not playlist_ids:
        raise HTTPException(
            status_code=400,
            detail="Não foi possível encontrar uma rota entre as faixas selecionadas com as transições disponíveis.",
        )

    resultado = []
    for track_id in playlist_ids:
        dados = grafo_global.nodes[track_id]
        resultado.append({
            "track_id": track_id,
            "nome": str(dados.get("track_name", "Desconhecido")),
            "artista": str(dados.get("artists", "Desconhecido")),
            "bpm": round(float(dados.get("tempo", 0.0) or 0.0), 3),
        })

    return {"playlist": resultado, "perfil": serializar_perfil(perfil)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_excludes=["data/*", "data/**"],
    )