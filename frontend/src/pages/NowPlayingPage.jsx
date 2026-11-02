import { Heart, MoreHorizontal, ListMusic, ChevronLeft, ChevronRight, Music2 } from "lucide-react";
import "./NowPlayingPage.css";

export default function NowPlayingPage({ current, queue, onPlay, likedIds, onLike, setPage }) {
  if (!current) {
    return <div className="now-playing-empty">Nenhuma música selecionada.</div>;
  }

  const isLiked = likedIds.includes(current.id || current.track_id);
  const currentImage = current.image || current.cover_url;
  const hasValidMainImage = currentImage && !currentImage.includes("placeholder") && currentImage !== "nan";

  const sugestoes = queue
    .filter((t) => (t.id || t.track_id) !== (current.id || current.track_id))
    .slice(0, 5);

  return (
    <div className="now-playing-container">
      
      {/* PAINEL ESQUERDO (Destaque com degradê) */}
      <div className="now-playing-main">
        <div className="now-playing-header">
          <div className="header-nav-buttons">
            <button className="nav-btn" onClick={() => setPage("home")} title="Voltar">
              <ChevronLeft size={20} />
            </button>
            <button className="nav-btn" disabled title="Avançar">
              <ChevronRight size={20} />
            </button>
          </div>
          <h2>Tocando Agora</h2>
          <div className="header-spacer"></div>
        </div>

        <div className="main-cover-wrapper">
          {hasValidMainImage ? (
            <img 
              src={currentImage} 
              alt={current.title || current.track_name || current.nome} 
              className="main-cover" 
            />
          ) : (
            <div className="main-cover empty-cover" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#222', borderRadius: '8px', width: '100%', aspectRatio: '1/1', boxShadow: '0 8px 24px rgba(0,0,0,0.5)' }}>
              <Music2 size={120} color="#444" />
            </div>
          )}
        </div>

        <div className="main-track-info">
          <div className="main-track-titles">
            <h1>{current.title || current.track_name || current.nome}</h1>
            <p>{current.artist || current.artist_name || current.artista}</p>
          </div>
          
          <div className="main-track-actions">
            <button onClick={() => onLike(current.id || current.track_id)} className="action-btn">
              <Heart size={24} fill={isLiked ? "currentColor" : "none"} className={isLiked ? "liked" : ""} />
            </button>
            <button className="action-btn">
              <MoreHorizontal size={24} />
            </button>
          </div>
        </div>

        <div className="fake-lyrics">
          <p>Letra não disponível no momento.</p>
          <p>Aproveite a sua vibe e deixe o som rolar...</p>
        </div>
      </div>

      {/* PAINEL DIREITO (Caixa de sugestões separada) */}
      <div className="now-playing-sidebar">
        <div className="sidebar-header">
          <h3>Sugeridas</h3>
          <button className="action-btn"><ListMusic size={20} /></button>
        </div>

        <p className="sidebar-subtitle">Sugeridas</p>

        <div className="suggested-list">
          {sugestoes.map((track) => {
            const trackImage = track.image || track.cover_url;
            const hasValidTrackImage = trackImage && !trackImage.includes("placeholder") && trackImage !== "nan";
            const trackTitle = track.title || track.track_name || track.nome;
            const trackArtist = track.artist || track.artist_name || track.artista;

            return (
              <div 
                key={track.id || track.track_id} 
                className="suggested-item" 
                onClick={() => onPlay(track)}
              >
                {hasValidTrackImage ? (
                  <img src={trackImage} alt={trackTitle} />
                ) : (
                  <div className="suggested-placeholder">
                    <Music2 size={20} color="#888" />
                  </div>
                )}
                <div className="suggested-info">
                  <h4>{trackTitle}</h4>
                  <p>{trackArtist}</p>
                </div>
                <span className="suggested-time">0:30</span>
                <button className="action-btn small" onClick={(e) => e.stopPropagation()}>
                  <MoreHorizontal size={16} />
                </button>
              </div>
            );
          })}
        </div>
      </div>
      
    </div>
  );
}