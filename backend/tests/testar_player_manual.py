import os
import webbrowser
import requests

API_URL = "http://127.0.0.1:8000"

# IDs específicos para o teste
payload = {
    "origem_id": "53ZLwlLA0AnSSS7d4a1dEW",
    "destino_id": "2RSHsoi04658QL5xgQVov3"
}

print(f"1. Solicitando rota A* ao servidor...")
print(f"   Origem:  {payload['origem_id']}")
print(f"   Destino: {payload['destino_id']}")

playlist = []
try:
    res = requests.post(f"{API_URL}/recomendar", json=payload)
    print(f"   Status Code do Backend: {res.status_code}")
    
    if res.status_code == 200:
        resposta = res.json()
        playlist = resposta.get("playlist", [])
        print(f"   Total de faixas na playlist: {len(playlist)}")
    else:
        print(f"   [ERRO API]: {res.json()}")
except Exception as e:
    print(f"   [ERRO] Falha ao conectar com a API: {e}")


def obter_previa_30s(nome, artista):
    """Busca o áudio de 30s na iTunes API pública."""
    try:
        primeiro_artista = artista.split(";")[0] if artista else ""
        query = f"{nome} {primeiro_artista}".strip()
        url = f"https://itunes.apple.com/search?term={requests.utils.quote(query)}&entity=song&limit=1"
        res = requests.get(url, timeout=4).json()
        resultados = res.get("results", [])
        if resultados:
            return resultados[0].get("previewUrl")
    except Exception:
        pass
    return None


# Montagem do Player HTML
html = """
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <title>Auditoria de Transição Específica (A*)</title>
    <style>
        body { background-color: #121212; color: #ffffff; font-family: Arial, sans-serif; display: flex; flex-direction: column; align-items: center; padding: 20px; }
        h1 { color: #1db954; margin-bottom: 5px; }
        p { color: #b3b3b3; margin-bottom: 25px; }
        .card { background: #181818; border-radius: 10px; padding: 15px; margin: 10px; width: 520px; border: 1px solid #282828; }
        .info { font-size: 1rem; color: #1db954; font-weight: bold; margin-bottom: 4px; }
        .artist { font-size: 0.85rem; color: #b3b3b3; margin-bottom: 8px; }
        .bpm { background: #282828; color: #fff; font-size: 0.75rem; padding: 3px 8px; border-radius: 4px; display: inline-block; margin-bottom: 10px; }
        audio { width: 100%; }
        .no-preview { color: #e74c3c; font-size: 0.8rem; margin-top: 5px; }
        .empty-alert { background: #e74c3c; color: white; padding: 15px; border-radius: 8px; }
    </style>
</head>
<body>
    <h1>Auditoria de Transição Sonora (A*)</h1>
    <p>Auditoria entre os IDs específicos selecionados</p>
"""

if not playlist:
    html += '<div class="empty-alert">Não foi possível calcular uma rota entre estas duas músicas. Verifique se ambos os IDs estão carregados no grafo em memória.</div>'
else:
    for i, faixa in enumerate(playlist, 1):
        nome = faixa.get("nome", "Faixa")
        artista = faixa.get("artista", "")
        bpm = faixa.get("bpm", "N/A")

        print(f"2. Buscando prévia 30s ({i}/{len(playlist)}): {nome}...")
        preview_url = obter_previa_30s(nome, artista)
        player_html = f'<audio controls src="{preview_url}"></audio>' if preview_url else '<div class="no-preview">Prévia de 30s indisponível</div>'

        html += f"""
        <div class="card">
            <div class="info">#{i}. {nome}</div>
            <div class="artist">Artista: {artista}</div>
            <div class="bpm">Métrica/BPM: {bpm}</div>
            {player_html}
        </div>
        """

html += "</body></html>"

caminho_html = os.path.join("tests", "player_previa.html")
with open(caminho_html, "w", encoding="utf-8") as f:
    f.write(html)

print("3. Abrindo o player no navegador...")
webbrowser.open("file://" + os.path.realpath(caminho_html))