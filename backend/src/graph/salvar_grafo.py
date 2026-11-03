import os
import pickle
from src.graph.graph import construir_grafo

def exportar_grafo():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    caminho_saida = os.path.join(BASE_DIR, 'data', 'grafo_knn.pkl')

    print("A calcular arestas do K-NN (isso roda apenas uma vez)...")
    grafo = construir_grafo(k_vizinhos=35, popularidade_minima=0)

    print(f"A salvar grafo no disco em: {caminho_saida}")
    
    # Garante que a pasta data existe antes de salvar
    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
    
    with open(caminho_saida, 'wb') as f:
        pickle.dump(grafo, f, protocol=pickle.HIGHEST_PROTOCOL)

    print("Grafo pré-computado e salvo com sucesso!")

if __name__ == "__main__":
    exportar_grafo()