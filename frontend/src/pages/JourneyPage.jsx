import { useState, useEffect } from "react";
import { ArrowRight, Music2, Route, Search } from "lucide-react";

import "./JourneyPage.css";

export default function JourneyPage() {
  const [listaMusicas, setListaMusicas] = useState([]);
  const [musicaInicial, setMusicaInicial] = useState("");
  const [musicaFinal, setMusicaFinal] = useState("");
  const [mensagem, setMensagem] = useState("");
  const [percurso, setPercurso] = useState([]);
  const [carregando, setCarregando] = useState(false);
  const [carregandoMusicas, setCarregandoMusicas] = useState(true);

  useEffect(() => {
    async function carregarMusicasDoBackend() {
      try {
        const resposta = await fetch("http://127.0.0.1:8000/musicas?limite=100");
        if (!resposta.ok) {
          throw new Error("Erro ao buscar faixas do servidor");
        }
        const dados = await resposta.json();
        setListaMusicas(dados.musicas || []);
      } catch (erro) {
        console.error(erro);
        setMensagem("Erro ao carregar a lista de músicas do backend.");
      } finally {
        setCarregandoMusicas(false);
      }
    }

    carregarMusicasDoBackend();
  }, []);

  const iniciarPercurso = async () => {
    if (!musicaInicial || !musicaFinal) {
      setMensagem("Escolha as duas músicas para continuar.");
      return;
    }

    if (musicaInicial === musicaFinal) {
      setMensagem("Escolha duas músicas diferentes.");
      return;
    }

    setMensagem("");
    setPercurso([]);
    setCarregando(true);

    try {
      const resposta = await fetch("http://127.0.0.1:8000/recomendar", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          origem_id: musicaInicial,
          destino_id: musicaFinal,
        }),
      });

      if (!resposta.ok) {
        const erroData = await resposta.json();
        throw new Error(erroData.detail || "Erro na resposta do servidor");
      }

      const dados = await resposta.json();
      setPercurso(dados.playlist || []);
    } catch (erro) {
      console.error(erro);
      setMensagem(
        typeof erro.message === "string"
          ? erro.message
          : "Falha ao calcular o percurso. Tente novamente."
      );
    } finally {
      setCarregando(false);
    }
  };

  return (
    <section className="journey-page">
      <div className="journey-heading">
        <span className="journey-label">
          <Route size={16} />
          PERCURSO MUSICAL
        </span>

        <h1>De uma música a outra.</h1>

        <p>
          Escolha onde começar e onde quer chegar.
          Encontre um caminho musical com transições graduais.
        </p>
      </div>

      <div className="journey-form">
        <label htmlFor="musica-inicial">
          <span>01 — Música inicial (A)</span>

          <select
            id="musica-inicial"
            value={musicaInicial}
            disabled={carregandoMusicas}
            onChange={(evento) => {
              setMusicaInicial(evento.target.value);
              setMensagem("");
            }}
          >
            <option value="">
              {carregandoMusicas ? "Carregando músicas do banco..." : "Escolha a primeira música"}
            </option>

            {listaMusicas.map((musica) => (
              <option key={musica.track_id} value={musica.track_id}>
                {musica.nome} — {musica.artista}
              </option>
            ))}
          </select>
        </label>

        <div className="journey-connector">
          <div />
          <ArrowRight size={20} />
          <div />
        </div>

        <label htmlFor="musica-final">
          <span>02 — Música final (B)</span>

          <select
            id="musica-final"
            value={musicaFinal}
            disabled={carregandoMusicas}
            onChange={(evento) => {
              setMusicaFinal(evento.target.value);
              setMensagem("");
            }}
          >
            <option value="">
              {carregandoMusicas ? "Carregando músicas do banco..." : "Escolha a música de destino"}
            </option>

            {listaMusicas.map((musica) => (
              <option key={musica.track_id} value={musica.track_id}>
                {musica.nome} — {musica.artista}
              </option>
            ))}
          </select>
        </label>

        <button
          className="journey-button"
          onClick={iniciarPercurso}
          disabled={carregando || carregandoMusicas}
        >
          <Search size={18} />
          {carregando ? "Calculando caminho..." : "Encontrar meu caminho"}
        </button>

        {mensagem && (
          <p className="journey-message" role="status">
            {mensagem}
          </p>
        )}
      </div>

      {percurso.length > 0 && (
        <div className="journey-result">
          <h2>Seu Percurso Musical ({percurso.length} faixas)</h2>
          
          <div className="journey-playlist">
            {percurso.map((item) => (
              <div key={item.track_id} className="journey-embed-card">
                <iframe
                  title={`Spotify Player - ${item.nome}`}
                  src={`https://open.spotify.com/embed/track/${item.track_id}?utm_source=generator&theme=0`}
                  width="100%"
                  height="80"
                  frameBorder="0"
                  allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
                  loading="lazy"
                />
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="journey-info">
        <div className="journey-info-icon">
          <Music2 size={22} />
        </div>

        <div>
          <h2>Uma música de cada vez</h2>
          <p>
            A proposta é conectar as músicas escolhidas por meio
            de faixas intermediárias semelhantes, evitando mudanças
            bruscas de ritmo.
          </p>
        </div>
      </div>
    </section>
  );
}