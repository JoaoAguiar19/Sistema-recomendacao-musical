
import { useState } from "react";
import { ArrowRight, Music2, Route, Search } from "lucide-react";

import { tracks } from "../data/tracks";
import "./JourneyPage.css";
import "./JourneyPage.css";

export default function JourneyPage() {
  const [musicaInicial, setMusicaInicial] = useState("");
  const [musicaFinal, setMusicaFinal] = useState("");
  const [mensagem, setMensagem] = useState("");

  const iniciarPercurso = () => {
    if (!musicaInicial || !musicaFinal) {
      setMensagem("Escolha as duas músicas para continuar.");
      return;
    }

    if (musicaInicial === musicaFinal) {
      setMensagem("Escolha duas músicas diferentes.");
      return;
    }

    setMensagem(
      "As músicas foram selecionadas. O cálculo do percurso será conectado ao algoritmo de recomendação do back-end."
    );
  };

  return (
    <section className="journey-page">
      <div className="journey-heading">
        <span className="journey-label">
          <Route size={16} />
          PERCURSO MUSICAL
        </span>

        <h1>De uma vibe a outra.</h1>

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
            onChange={(evento) => {
              setMusicaInicial(evento.target.value);
              setMensagem("");
            }}
          >
            <option value="">Escolha a primeira música</option>

            {tracks.map((musica) => (
              <option key={musica.id} value={String(musica.id)}>
                {musica.title} — {musica.artist}
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
          <span>02 — Música de destino (B)</span>

          <select
            id="musica-final"
            value={musicaFinal}
            onChange={(evento) => {
              setMusicaFinal(evento.target.value);
              setMensagem("");
            }}
          >
            <option value="">Escolha a música de destino</option>

            {tracks.map((musica) => (
              <option key={musica.id} value={String(musica.id)}>
                {musica.title} — {musica.artist}
              </option>
            ))}
          </select>
        </label>

        <button
          className="journey-button"
          onClick={iniciarPercurso}
        >
          <Search size={18} />
          Encontrar meu caminho
        </button>

        {mensagem && (
          <p className="journey-message" role="status">
            {mensagem}
          </p>
        )}
      </div>

      <div className="journey-info">
        <div className="journey-info-icon">
          <Music2 size={22} />
        </div>

        <div>
          <h2>Uma música de cada vez</h2>
          <p>
            A proposta é conectar as músicas escolhidas por meio
            de faixas intermediárias semelhantes, evitando mudanças
            bruscas de ritmo. O percurso real aparecerá quando o
            algoritmo do back-end estiver integrado.
          </p>
        </div>
      </div>
    </section>
  );
}
