import { useState, useEffect } from "react";
import { ChevronRight, Clock3, Music2, Play } from "lucide-react";
import TrackRow from "../components/TrackRow";
import { mixes } from "../data/tracks";

export default function HomePage({ current, isPlaying, onPlay, likedIds, onLike, setPage }) {
  const [tracksEmAlta, setTracksEmAlta] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isGeneratingMix, setIsGeneratingMix] = useState(false);

  useEffect(() => {
    const fetchHomeData = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/home/populares"); 
        const data = await response.json();
        setTracksEmAlta(Array.isArray(data) ? data : []);
      } catch (error) {
        console.error("Erro ao buscar músicas da Home:", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchHomeData();
  }, []);

  const handlePlayAndNavigate = (track) => {
    // AGORA SIM: Enviamos a faixa clicada E a lista completa de sugestões!
    onPlay(track, tracksEmAlta);
    setPage("now-playing");
  };

  const handleMixClick = async (index) => {
    if (isGeneratingMix) return;
    setIsGeneratingMix(true);
    try {
      const perfis = ["crescente", "acelerar", "desacelerar", "estavel"];
      const percursoId = perfis[index % perfis.length];

      const response = await fetch("http://localhost:8000/recomendar-percurso", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ percurso_id: percursoId })
      });
      
      const data = await response.json();
      
      if (data.playlist && data.playlist.length > 0) {
        const queue = data.playlist.map(item => ({
          id: item.track_id,
          title: item.nome,
          artist: item.artista,
          time: "0:30",
          image: item.cover_url || "https://via.placeholder.com/60",
          preview_url: item.preview_url,
        }));
        
        onPlay(queue[0], queue);
        setPage("now-playing");
      }
    } catch (err) {
      console.error("Erro ao gerar percurso pelo Mix:", err);
    } finally {
      setIsGeneratingMix(false);
    }
  };

  return (
    <>
      <section className="hero">
        <div className="hero-copy">
          <span className="eyebrow"><span className="eyebrow-dot" />SUA TRILHA, SEU MOMENTO</span>
          <h1>A vida fica<br /><span>melhor com música.</span></h1>
          <p>Encontre a música certa para cada momento do seu dia.</p>
          <button
            className="primary-button"
            onClick={() => tracksEmAlta.length > 0 && handlePlayAndNavigate(tracksEmAlta[0])}
            disabled={isLoading}
          >
            <Play size={17} fill="currentColor" /> Começar a ouvir
          </button>
        </div>
        <div className="hero-art" aria-hidden="true">
          <div className="hero-orbit orbit-one" /><div className="hero-orbit orbit-two" />
          <div className="hero-disc"><div className="disc-center"><Music2 size={38} /></div></div>
          <div className="floating-note note-one">♪</div><div className="floating-note note-two">♫</div>
          <div className="hero-glow" />
        </div>
      </section>

      <section className="content-section">
        <div className="section-heading">
          <div><span className="section-kicker">SELEÇÃO PARA VOCÊ</span><h2>Encontre sua vibe</h2></div>
          <button className="text-button" onClick={() => setPage("journey")}>Ver tudo <ChevronRight size={16} /></button>
        </div>

        <div className="mix-grid">
          {mixes.map((mix, index) => (
            <button
              className="mix-card"
              key={mix.title}
              onClick={() => handleMixClick(index)}
              disabled={isGeneratingMix}
            >
              <div className="mix-art">
                <img src={mix.image} alt="" />
                <span className="mix-index">0{index + 1}</span>
                <span className="card-play"><Play size={20} fill="currentColor" /></span>
              </div>
              <strong>{mix.title}</strong>
              <span>{isGeneratingMix ? "A calcular rota..." : mix.subtitle}</span>
            </button>
          ))}
        </div>
      </section>

      <section className="content-section tracks-section">
        <div className="section-heading">
          <div><span className="section-kicker">TOQUE E DESCUBRA</span><h2>Em alta</h2></div>
          <button className="text-button" onClick={() => setPage("search")}>Explorar músicas <ChevronRight size={16} /></button>
        </div>

        <div className="track-table">
          <div className="track-header">
            <span>#</span><span>TÍTULO</span><span>ÁLBUM</span><span><Clock3 size={15} /></span><span />
          </div>
          {isLoading ? (
            <div style={{ padding: "2rem", color: "var(--text-muted)" }}>A carregar hits...</div>
          ) : (
            tracksEmAlta.map((track, index) => (
              <TrackRow
                key={track.id} track={track} index={index}
                current={current} isPlaying={isPlaying}
                onPlay={() => handlePlayAndNavigate(track)}
                liked={likedIds.includes(track.id)} onLike={onLike}
              />
            ))
          )}
        </div>
      </section>
    </>
  );
}