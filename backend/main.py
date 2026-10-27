from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from src.graph.graph import construir_grafo
from src.algoritmos.busca_astar import gerar_playlist_astar

app = FastAPI(title="Sistema de Recomendação Musical")

grafo_global = None

@app.on_event("startup")
def startup_event():
    global grafo_global
    print("A iniciar o servidor e a construir o grafo K-NN em memória...")
    grafo_global = construir_grafo(k_vizinhos=35, popularidade_minima=40)
    
    nos_carregados = list(grafo_global.nodes)
    print(f"Total de nós no grafo final: {len(nos_carregados)}")


@app.get("/amostra")
def obter_amostra_nos():
    """Retorna duas músicas válidas diretamente do grafo em memória para o teste."""
    if not grafo_global or len(grafo_global.nodes) < 2:
        raise HTTPException(status_code=500, detail="O grafo ainda não foi carregado.")
    
    nos = list(grafo_global.nodes)
    origem_id = nos[0]
    destino_id = nos[-1]
    
    return {
        "origem": {
            "id": origem_id,
            "nome": grafo_global.nodes[origem_id].get("track_name", "Desconhecido"),
            "artista": grafo_global.nodes[origem_id].get("artists", "Desconhecido"),
            "genero": grafo_global.nodes[origem_id].get("track_genre", "N/A")
        },
        "destino": {
            "id": destino_id,
            "nome": grafo_global.nodes[destino_id].get("track_name", "Desconhecido"),
            "artista": grafo_global.nodes[destino_id].get("artists", "Desconhecido"),
            "genero": grafo_global.nodes[destino_id].get("track_genre", "N/A")
        }
    }


@app.get("/musicas")
def listar_musicas(
    limite: int = Query(default=50, ge=1, le=500),
    busca: Optional[str] = Query(default=None, description="Filtra por nome da música ou artista"),
    genero: Optional[str] = Query(default=None, description="Filtra por gênero (ex: rock, pop, forro)")
):
    """Retorna a lista de faixas ativas no grafo em memória RAM."""
    if not grafo_global:
        raise HTTPException(status_code=500, detail="O grafo ainda não foi inicializado.")

    resultado = []
    termo_busca = busca.lower() if busca else None
    termo_genero = genero.lower() if genero else None

    for track_id, dados in grafo_global.nodes(data=True):
        nome = str(dados.get("track_name", ""))
        artista = str(dados.get("artists", ""))
        track_genre = str(dados.get("track_genre", ""))

        if termo_busca and (termo_busca not in nome.lower() and termo_busca not in artista.lower()):
            continue

        if termo_genero and termo_genero != track_genre.lower():
            continue

        resultado.append({
            "track_id": track_id,
            "nome": nome,
            "artista": artista,
            "genero": track_genre,
            "popularidade": dados.get("popularity", 0),
            "bpm": round(float(dados.get("tempo", 0)), 3)
        })

        if len(resultado) >= limite:
            break

    return {
        "total_grafo": len(grafo_global.nodes),
        "total_exibido": len(resultado),
        "musicas": resultado
    }


class RecomendacaoRequest(BaseModel):
    origem_id: str
    destino_id: str


@app.post("/recomendar")
def recomendar_playlist(request: RecomendacaoRequest):
    if not grafo_global:
        raise HTTPException(status_code=500, detail="O grafo ainda não foi inicializado.")

    if request.origem_id not in grafo_global.nodes or request.destino_id not in grafo_global.nodes:
        raise HTTPException(status_code=404, detail="Música de origem ou destino não encontrada no grafo.")
    
    playlist = gerar_playlist_astar(grafo_global, request.origem_id, request.destino_id)
    
    if not playlist:
        raise HTTPException(status_code=400, detail="Não foi possível traçar uma rota contínua entre as faixas.")
    
    resultado = []
    for track_id in playlist:
        dados_no = grafo_global.nodes[track_id]
        resultado.append({
            "track_id": track_id,
            "nome": dados_no.get("track_name", "Desconhecido"),
            "artista": dados_no.get("artists", "Desconhecido"),
            "bpm": round(float(dados_no.get("tempo", 0)), 3)
        })
        
    return {
        "total_faixas": len(resultado),
        "playlist": resultado
    }