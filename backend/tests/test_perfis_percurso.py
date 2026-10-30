import unittest

import networkx as nx

from src.algoritmos.busca_astar import gerar_playlist_astar
from src.algoritmos.custos_trajeto import calcular_peso_aresta
from src.algoritmos.heuristica_astar import heuristica_astar
from src.algoritmos.metricas_audio import (
    MAX_DIFERENCA_ENERGIA,
    MAX_DIFERENCA_TEMPO,
    PESO_BPM,
    PESO_ENERGIA,
    PESO_ESTILO,
    PESO_HARMONIA,
    PESO_POPULARIDADE,
    calcular_custo_bpm,
    calcular_custo_energia,
)
from src.algoritmos.perfis_percurso import PERFIS_PERCURSO
from src.graph.graph import filtrar_transicoes_bruscas


def atributos_musica(tempo, energia, popularidade=100):
    return {
        "tempo": tempo,
        "energy": energia,
        "valence": 0.5,
        "danceability": 0.5,
        "loudness": 0.5,
        "speechiness": 0.1,
        "acousticness": 0.2,
        "instrumentalness": 0.1,
        "liveness": 0.2,
        "key": 0,
        "mode": 1,
        "popularity": popularidade,
    }


class TestTransicoesMusicais(unittest.TestCase):
    def test_custo_de_bpm_e_energia_e_simetrico(self):
        self.assertEqual(calcular_custo_bpm(0.2, 0.3), calcular_custo_bpm(0.3, 0.2))
        self.assertEqual(
            calcular_custo_energia(0.2, 0.3),
            calcular_custo_energia(0.3, 0.2),
        )
        self.assertEqual(calcular_custo_bpm(0.4, 0.4), 0.0)
        self.assertEqual(calcular_custo_energia(0.4, 0.4), 0.0)

    def test_peso_da_aresta_combina_todas_as_metricas(self):
        grafo = nx.Graph()
        grafo.add_node("a", **atributos_musica(0.2, 0.2, popularidade=100))
        grafo.add_node("b", **atributos_musica(0.2, 0.2, popularidade=100))

        self.assertEqual(
            calcular_peso_aresta(grafo, "a", "b", {"weight": 0.0}), 0.0
        )

        grafo.nodes["b"]["tempo"] = 0.28
        self.assertGreater(
            calcular_peso_aresta(grafo, "a", "b", {"weight": 0.0}),
            PESO_BPM * 0.99,
        )
        grafo.nodes["b"]["tempo"] = 0.2
        grafo.nodes["b"]["energy"] = 0.35
        self.assertGreater(
            calcular_peso_aresta(grafo, "a", "b", {"weight": 0.0}),
            PESO_ENERGIA * 0.99,
        )
        grafo.nodes["b"]["energy"] = 0.2
        grafo.nodes["b"]["key"] = 6
        self.assertGreater(
            calcular_peso_aresta(grafo, "a", "b", {"weight": 0.0}),
            PESO_HARMONIA * 0.9,
        )
        grafo.nodes["b"]["key"] = 0
        grafo.nodes["b"]["popularity"] = 0
        self.assertAlmostEqual(
            calcular_peso_aresta(grafo, "a", "b", {"weight": 0.0}),
            PESO_POPULARIDADE,
        )
        grafo.nodes["b"]["popularity"] = 100
        self.assertAlmostEqual(
            calcular_peso_aresta(grafo, "a", "b", {"weight": 2.0}),
            PESO_ESTILO,
        )

    def test_filtro_remove_saltos_fora_das_faixas_normalizadas(self):
        grafo = nx.Graph()
        grafo.add_node("a", **atributos_musica(0.2, 0.2))
        grafo.add_node(
            "b",
            **atributos_musica(0.2 + MAX_DIFERENCA_TEMPO, 0.2 + MAX_DIFERENCA_ENERGIA),
        )
        grafo.add_node("c", **atributos_musica(0.2 + MAX_DIFERENCA_TEMPO + 0.001, 0.2))
        grafo.add_edge("a", "b", weight=0.1)
        grafo.add_edge("a", "c", weight=0.1)

        filtrar_transicoes_bruscas(grafo)

        self.assertTrue(grafo.has_edge("a", "b"))
        self.assertFalse(grafo.has_edge("a", "c"))

    def test_astar_retorna_caminho_de_menor_custo_acumulado(self):
        grafo = nx.Graph()
        musicas = {
            "inicio": (0.20, 0.20),
            "ponte1": (0.24, 0.25),
            "ponte2": (0.28, 0.30),
            "fim": (0.32, 0.35),
        }
        for track_id, (tempo, energia) in musicas.items():
            grafo.add_node(track_id, **atributos_musica(tempo, energia))

        grafo.add_edge("inicio", "fim", weight=0.1)
        grafo.add_edge("inicio", "ponte1", weight=0.0)
        grafo.add_edge("ponte1", "ponte2", weight=0.0)
        grafo.add_edge("ponte2", "fim", weight=0.0)

        def custo_aresta(atual, vizinho, dados):
            return calcular_peso_aresta(grafo, atual, vizinho, dados)

        caminho_astar = gerar_playlist_astar(grafo, "inicio", "fim")
        caminho_dijkstra = nx.dijkstra_path(
            grafo, "inicio", "fim", weight=custo_aresta
        )

        self.assertEqual(caminho_astar, caminho_dijkstra)
        self.assertEqual(caminho_astar, ["inicio", "ponte1", "ponte2", "fim"])

    def test_heuristica_e_admissivel_para_custos_combinados(self):
        grafo = nx.Graph()
        grafo.add_node("a", **atributos_musica(0.2, 0.3))
        grafo.add_node("b", **atributos_musica(0.9, 0.8))

        self.assertEqual(heuristica_astar(grafo, "a", "b"), 0.0)

    def test_perfis_usam_intervalos_bpm_normalizados_sem_etapas_de_energia(self):
        for perfil in PERFIS_PERCURSO:
            self.assertNotIn("categorias", perfil)
            for intervalo in (perfil["bpm_inicial"], perfil["bpm_final"]):
                self.assertGreaterEqual(intervalo["min"], 0.0)
                self.assertLessEqual(intervalo["max"], 1.0)
                self.assertLessEqual(intervalo["min"], intervalo["max"])


if __name__ == "__main__":
    unittest.main()
