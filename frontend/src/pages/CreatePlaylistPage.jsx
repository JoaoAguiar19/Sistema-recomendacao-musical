import { Music2, Play, Plus, Sparkles } from "lucide-react";
import { tracks } from "../data/tracks";
import "./CreatePlaylistPage.css";

const previewTracks = tracks.slice(0, 3);

export default function CreatePlaylistPage() {
  return (
    <section className="simple-page create-playlist-page">
      <span className="section-kicker">SUA COLEÇÃO</span>
      <h1>Criar playlist</h1>
      <p className="page-description">
        Uma prévia visual de como sua playlist pode ficar.
      </p>

      <div className="playlist-preview">
        <div className="playlist-preview-heading">
          <div>
            <span className="playlist-preview-eyebrow">
              <Sparkles size={14} /> PRÉVIA DA PLAYLIST
            </span>
            <h2>Seu próximo som começa aqui</h2>
          </div>
          <span className="playlist-demo-badge">DEMONSTRAÇÃO</span>
        </div>

        <div className="playlist-preview-card">
          <div className="playlist-preview-art" aria-hidden="true">
            {previewTracks.map((track) => (
              <img key={track.id} src={track.image} alt="" />
            ))}
            <span className="playlist-preview-art-icon">
              <Music2 size={30} />
            </span>
          </div>

          <div className="playlist-preview-details">
            <span className="playlist-preview-type">PLAYLIST PESSOAL</span>
            <h3>Fim de tarde</h3>
            <p>Uma seleção para desacelerar e aproveitar o momento.</p>
            <div className="playlist-preview-meta">
              <span>3 músicas</span>
              <span className="playlist-meta-dot" />
              <span>criada por você</span>
            </div>
          </div>

          <span className="playlist-preview-play" aria-hidden="true">
            <Play size={22} fill="currentColor" />
          </span>
        </div>

        <div className="playlist-preview-list">
          <div className="playlist-preview-list-heading">
            <span>FAIXAS</span>
            <span>TÍTULO</span>
            <span>ÁLBUM</span>
          </div>
          {previewTracks.map((track, index) => (
            <div className="playlist-preview-row" key={track.id}>
              <span className="playlist-preview-number">
                {String(index + 1).padStart(2, "0")}
              </span>
              <img src={track.image} alt="" />
              <div className="playlist-preview-track-info">
                <strong>{track.title}</strong>
                <span>{track.artist}</span>
              </div>
              <span className="playlist-preview-album">{track.album}</span>
              <span className="playlist-preview-duration">{track.time}</span>
            </div>
          ))}
          <div className="playlist-preview-add">
            <span className="playlist-preview-add-icon">
              <Plus size={17} />
            </span>
            <span>
              <strong>Adicionar músicas</strong>
              <small>As faixas escolhidas aparecerão aqui</small>
            </span>
          </div>
        </div>
      </div>
    </section>
  );
}
