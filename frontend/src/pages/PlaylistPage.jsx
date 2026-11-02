import { Disc3, ListMusic, LockKeyhole, Plus, Sparkles } from "lucide-react";
import "./PlaylistPage.css";

export default function PlaylistPage() {
  return (
    <section className="playlist-page">
      <div className="playlist-page-heading">
        <span className="section-kicker">SUA COLEÇÃO</span>
        <h1>Uma playlist para cada momento.</h1>
        <p>Crie trilhas sonoras com as músicas que combinam com você.</p>
      </div>

      <div className="playlist-builder">
        <div className="playlist-builder-main">
          <div className="playlist-artwork">
            <div className="playlist-artwork-glow" />
            <Disc3 size={76} strokeWidth={1.1} />
            <span className="playlist-artwork-note">♫</span>
          </div>

          <div className="playlist-builder-copy">
            <span className="playlist-overline">NOVA PLAYLIST</span>
            <h2>Sua próxima vibe começa aqui</h2>
            <p>
              Dê um nome à sua playlist e reúna as faixas perfeitas para
              acompanhar cada momento.
            </p>

            <div className="playlist-detail-preview">
              <span>Nome da playlist</span>
              <strong>Minha nova playlist</strong>
            </div>
            <div className="playlist-detail-preview playlist-description-preview">
              <span>Descrição</span>
              <strong>Uma seleção feita por você.</strong>
            </div>

            <div className="playlist-privacy">
              <LockKeyhole size={15} />
              <span>Playlist privada</span>
            </div>
          </div>
        </div>

        <div className="playlist-builder-footer">
          <div className="playlist-ready-label">
            <Sparkles size={16} />
            <span>Seu espaço, suas escolhas</span>
          </div>
          <span className="playlist-coming-soon">EDIÇÃO EM BREVE</span>
        </div>
      </div>

      <div className="playlist-empty-panel">
        <div className="playlist-empty-icon">
          <ListMusic size={22} />
        </div>
        <div className="playlist-empty-copy">
          <h3>As suas músicas vão aparecer aqui</h3>
          <p>Adicione faixas para montar uma sequência só sua.</p>
        </div>
        <button className="playlist-add-button" type="button" disabled>
          <Plus size={17} />
          Adicionar músicas
          <span>Em breve</span>
        </button>
      </div>
    </section>
  );
}
