
import {
  ChevronRight,
  Clock3,
  Music2,
  Play,
} from "lucide-react";

import TrackRow from "../components/TrackRow";
import { tracks, mixes } from "../data/tracks";

export default function HomePage({
  current,
  isPlaying,
  onPlay,
  likedIds,
  onLike,
  setPage,
}) {
  return (
    <>
      <section className="hero">
        <div className="hero-copy">
          <span className="eyebrow">
            <span className="eyebrow-dot" />
            SUA TRILHA, SEU MOMENTO
          </span>

          <h1>
            A vida fica
            <br />
            <span>melhor com música.</span>
          </h1>

          <p>
            Encontre a vibe certa para cada momento do seu dia.
          </p>

          <button
            className="primary-button"
            onClick={() => onPlay(tracks[0])}
          >
            <Play size={17} fill="currentColor" />
            Começar a ouvir
          </button>
        </div>

        <div className="hero-art" aria-hidden="true">
          <div className="hero-orbit orbit-one" />
          <div className="hero-orbit orbit-two" />

          <div className="hero-disc">
            <div className="disc-center">
              <Music2 size={38} />
            </div>
          </div>

          <div className="floating-note note-one">♪</div>
          <div className="floating-note note-two">♫</div>
          <div className="hero-glow" />
        </div>

        <div className="hero-tag">
          <span className="tag-pulse" />
          FEITO PARA SUA VIBE
        </div>
      </section>

      <section className="content-section">
        <div className="section-heading">
          <div>
            <span className="section-kicker">
              SELEÇÃO PARA VOCÊ
            </span>
            <h2>Encontre sua vibe</h2>
          </div>

          <button
            className="text-button"
            onClick={() => setPage("search")}
          >
            Ver tudo <ChevronRight size={16} />
          </button>
        </div>

        <div className="mix-grid">
          {mixes.map((mix, index) => (
            <button
              className="mix-card"
              key={mix.title}
              onClick={() => onPlay(tracks[index % tracks.length])}
            >
              <div className="mix-art">
                <img src={mix.image} alt="" />

                <span className="mix-index">
                  0{index + 1}
                </span>

                <span className="card-play">
                  <Play size={20} fill="currentColor" />
                </span>
              </div>

              <strong>{mix.title}</strong>
              <span>{mix.subtitle}</span>
            </button>
          ))}
        </div>
      </section>

      <section className="content-section tracks-section">
        <div className="section-heading">
          <div>
            <span className="section-kicker">
              TOQUE E DESCUBRA
            </span>
            <h2>Em alta agora</h2>
          </div>

          <button
            className="text-button"
            onClick={() => setPage("search")}
          >
            Explorar músicas <ChevronRight size={16} />
          </button>
        </div>

        <div className="track-table">
          <div className="track-header">
            <span>#</span>
            <span>TÍTULO</span>
            <span>ÁLBUM</span>
            <span>
              <Clock3 size={15} />
            </span>
            <span />
          </div>

          {tracks.map((track, index) => (
            <TrackRow
              key={track.id}
              track={track}
              index={index}
              current={current}
              isPlaying={isPlaying}
              onPlay={onPlay}
              liked={likedIds.includes(track.id)}
              onLike={onLike}
            />
          ))}
        </div>
      </section>
    </>
  );
}
