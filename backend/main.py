from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.algoritmos.grafo import construir_grafo, gerar_playlist_astar

app = FastAPI(title="Sistema de Recomendação Musical")

# Variável global para manter o grafo em memória e evitar recálculos a cada requisição
grafo_global = None

@app.on_event("startup")
def startup_event():
    global grafo_global
    print("A iniciar o servidor e a construir o grafo K-NN em memória...")
    grafo_global = construir_grafo(k_vizinhos=15)
    
    # Diagnóstico para inspecionar os IDs reais na RAM
    nos_carregados = list(grafo_global.nodes)
    print(f"Total de nós carregados: {len(nos_carregados)}")
    if nos_carregados:
        print("Exemplos exatos de IDs no grafo:", nos_carregados[:5])

class RecomendacaoRequest(BaseModel):
    origem_id: str
    destino_id: str

@app.post("/recomendar")
def recomendar_playlist(request: RecomendacaoRequest):
    if request.origem_id not in grafo_global.nodes or request.destino_id not in grafo_global.nodes:
        raise HTTPException(status_code=404, detail="Música de origem ou destino não encontrada no grafo.")
    
    playlist = gerar_playlist_astar(grafo_global, request.origem_id, request.destino_id)
    
    if not playlist:
        raise HTTPException(status_code=400, detail="Não foi possível traçar uma rota contínua entre as faixas.")
    
    # Estrutura a resposta JSON consumível pelo front-end
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