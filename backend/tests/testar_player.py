import requests
import webbrowser
import os

# Altere os IDs aqui para testar novas rotas
payload = {"origem_id": "6EEDuy7cieppsAqgEvCkkL", "destino_id": "5KV9bNW1Ta4Z4PdHgu84TA"}
resposta = requests.post("http://127.0.0.1:8000/recomendar", json=payload).json()

html = "<html><body style='background:#121212; color:white; text-align:center; font-family:sans-serif;'>"
html += "<h1>Degradê Sonoro</h1>"

for faixa in resposta.get("playlist", []):
    track_id = faixa["track_id"]
    html += f'<iframe src="https://open.spotify.com/embed/track/{track_id}" width="300" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media" style="margin: 10px;"></iframe><br>'

html += "</body></html>"

with open("player_teste.html", "w") as f:
    f.write(html)

webbrowser.open('file://' + os.path.realpath("player_teste.html"))