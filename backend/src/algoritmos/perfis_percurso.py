PERFIS_PERCURSO = [
    {
        "id": "energia-crescente",
        "nome": "Ritmo crescente",
        "descricao": "Conecte faixas de BPM mais baixo a faixas de BPM mais alto.",
        "bpm_inicial": {"min": 0.28, "max": 0.38},
        "bpm_final": {"min": 0.52, "max": 0.64},
    },
    {
        "id": "ganhar-ritmo",
        "nome": "Acelerar o ritmo",
        "descricao": "Uma conexao entre faixas de BPM moderado e mais acelerado.",
        "bpm_inicial": {"min": 0.36, "max": 0.48},
        "bpm_final": {"min": 0.50, "max": 0.64},
    },
    {
        "id": "desacelerar",
        "nome": "Desacelerar o ritmo",
        "descricao": "Conecte faixas de BPM mais alto a faixas de BPM mais baixo.",
        "bpm_inicial": {"min": 0.52, "max": 0.68},
        "bpm_final": {"min": 0.26, "max": 0.38},
    },
    {
        "id": "ondas-suaves",
        "nome": "Ritmo estavel",
        "descricao": "Conecte faixas em intervalos de BPM semelhantes.",
        "bpm_inicial": {"min": 0.36, "max": 0.50},
        "bpm_final": {"min": 0.36, "max": 0.50},
    },
]


def obter_perfil(perfil_id):
    return next((perfil for perfil in PERFIS_PERCURSO if perfil["id"] == perfil_id), None)


def serializar_perfil(perfil):
    return dict(perfil)
