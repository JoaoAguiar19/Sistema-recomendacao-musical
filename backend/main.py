from typing import Optional
import requests
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from src.graph.graph import construir_grafo
from src.algoritmos.busca_astar import gerar_playlist_astar

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Sistema de Recomendação Musical")

# Habilita o CORS para o React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

grafo_global = None


def buscar_previa_itunes(nome: str, artista: str) -> Optional[str]:
    """Busca a URL de prévia de áudio (30s) na API do iTunes Search."""
    try:
        primeiro_artista = artista.split(";")[0] if artista else ""
        query = f"{nome} {primeiro_artista}".strip()
        url = f"https://itunes.apple.com/search?term={requests.utils.quote(query)}&entity=song&limit=1"
        res = requests.get(url, timeout=3).json()
        resultados = res.get("results", [])
        if resultados:
            return resultados[0].get("previewUrl")
    except Exception:
        pass
    return None


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
    
    origem_nome = grafo_global.nodes[origem_id].get("track_name", "Desconhecido")
    origem_artista = grafo_global.nodes[origem_id].get("artists", "Desconhecido")
    
    destino_nome = grafo_global.nodes[destino_id].get("track_name", "Desconhecido")
    destino_artista = grafo_global.nodes[destino_id].get("artists", "Desconhecido")

    return {
        "origem": {
            "id": origem_id,
            "nome": origem_nome,
            "artista": origem_artista,
            "genero": grafo_global.nodes[origem_id].get("track_genre", "N/A"),
            "audio_url": (
                grafo_global.nodes[origem_id].get("preview_url") 
                or grafo_global.nodes[origem_id].get("audio_url") 
                or buscar_previa_itunes(origem_nome, origem_artista)
            )
        },
        "destino": {
            "id": destino_id,
            "nome": destino_nome,
            "artista": destino_artista,
            "genero": grafo_global.nodes[destino_id].get("track_genre", "N/A"),
            "audio_url": (
                grafo_global.nodes[destino_id].get("preview_url") 
                or grafo_global.nodes[destino_id].get("audio_url") 
                or buscar_previa_itunes(destino_nome, destino_artista)
            )
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
            "bpm": round(float(dados.get("tempo", 0)), 3),
            "audio_url": dados.get("preview_url") or dados.get("audio_url")
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
        nome = dados_no.get("track_name", "Desconhecido")
        artista = dados_no.get("artists", "Desconhecido")

        # Tenta obter do banco ou busca via iTunes API em tempo real
        audio = (
            dados_no.get("preview_url") 
            or dados_no.get("audio_url") 
            or buscar_previa_itunes(nome, artista)
        )

        resultado.append({
            "track_id": track_id,
            "nome": nome,
            "artista": artista,
            "bpm": round(float(dados_no.get("tempo", 0)), 3),
            "audio_url": audio
        })
        
    return {
        "total_faixas": len(resultado),
        "playlist": resultado
    }