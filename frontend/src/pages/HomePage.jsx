import { useState, useEffect, useRef } from "react";
import { ChevronRight, Clock3, Music2, Play, Search, X } from "lucide-react";
import TrackRow from "../components/TrackRow";
import { mixes } from "../data/tracks";
import { obterMusicas, obterPrevia, obterRecomendacoes } from "../services/musicaService";

const SEARCH_PAGE_SIZE = 50;

export default function HomePage({
  current,
  isPlaying,
  onPlay,
  onSearchPlay,
  searchOpen,
  onToggleSearch,
  likedIds,
  onLike,
  setPage,
}) {
  const [tracksEmAlta, setTracksEmAlta] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [generatingMixTitle, setGeneratingMixTitle] = useState("");
  const [mixError, setMixError] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [searchTotal, setSearchTotal] = useState(0);
  const [isSearching, setIsSearching] = useState(false);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [searchError, setSearchError] = useState("");
  const [selectingTrackId, setSelectingTrackId] = useState(null);
  const searchVersion = useRef(0);

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

  useEffect(() => {
    const query = searchQuery.trim();
    if (!searchOpen || query.length < 2) return undefined;

    let active = true;
    const timeoutId = window.setTimeout(async () => {
      setIsSearching(true);
      setSearchError("");
      try {
        const data = await obterMusicas(query, SEARCH_PAGE_SIZE);
        if (active) {
          setSearchResults(Array.isArray(data.musicas) ? data.musicas : []);
          setSearchTotal(Number(data.total) || 0);
        }
      } catch (error) {
        if (active) {
          console.error("Erro ao buscar músicas:", error);
          setSearchError("Não foi possível buscar músicas. Verifique a conexão com o servidor.");
        }
      } finally {
        if (active) setIsSearching(false);
      }
    }, 300);

    return () => {
      active = false;
      window.clearTimeout(timeoutId);
    };
  }, [searchOpen, searchQuery]);

  const handleSearchQueryChange = (event) => {
    searchVersion.current += 1;
    setSearchQuery(event.target.value);
    setSearchResults([]);
    setSearchTotal(0);
    setSearchError("");
  };

  const handleLoadMoreSearchResults = async () => {
    if (isLoadingMore || searchResults.length >= searchTotal) return;
    const requestVersion = searchVersion.current;
    setIsLoadingMore(true);
    setSearchError("");
    try {
      const data = await obterMusicas(
        searchQuery.trim(),
        SEARCH_PAGE_SIZE,
        searchResults.length
      );
      const nextResults = Array.isArray(data.musicas) ? data.musicas : [];
      if (requestVersion === searchVersion.current) {
        setSearchResults((results) => [...results, ...nextResults]);
        setSearchTotal(Number(data.total) || 0);
      }
    } catch (error) {
      if (requestVersion === searchVersion.current) {
        console.error("Erro ao carregar mais músicas:", error);
        setSearchError("Não foi possível carregar mais músicas. Tente novamente.");
      }
    } finally {
      setIsLoadingMore(false);
    }
  };

  const normalizeTrack = (track) => ({
    id: track.track_id || track.id,
    track_id: track.track_id || track.id,
    title: track.nome || track.title,
    artist: track.artista || track.artist,
    time: "0:30",
    image: track.image || track.cover_url,
    cover_url: track.cover_url || track.image,
    preview_url: track.preview_url,
  });

  const handleSearchTrackPlay = async (result) => {
    let track = normalizeTrack(result);
    setSelectingTrackId(track.id);
    setSearchError("");
    try {
      if (!track.preview_url) {
        const previewUrl = await obterPrevia(track.title, track.artist);
        if (!previewUrl) {
          setSearchError("Esta faixa não tem prévia disponível e não pode ser reproduzida.");
          return;
        }
        track = { ...track, preview_url: previewUrl };
      }

      try {
        const suggestions = await obterRecomendacoes(track.id);
        onSearchPlay(
          track,
          suggestions.map(normalizeTrack).filter((suggestion) => suggestion.preview_url)
        );
      } catch (error) {
        console.error("Erro ao buscar músicas próximas:", error);
        onSearchPlay(
          track,
          [],
          "A faixa será reproduzida, mas não foi possível carregar as sugestões."
        );
      }
    } catch (error) {
      console.error("Erro ao verificar a prévia da faixa:", error);
      setSearchError("Não foi possível verificar a prévia desta faixa. Tente novamente.");
    } finally {
      setSelectingTrackId(null);
    }
  };

  const handlePlayAndNavigate = (track) => {
    // AGORA SIM: Enviamos a faixa clicada E a lista completa de sugestões!
    onPlay(track, tracksEmAlta);
    setPage("now-playing");
  };

  const handleMixClick = async (mix) => {
    if (generatingMixTitle) return;
    setGeneratingMixTitle(mix.title);
    setMixError("");
    try {
      const response = await fetch("http://localhost:8000/recomendar-percurso", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ percurso_id: mix.percursoId })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Não foi possível gerar este percurso.");
      }

      const data = await response.json();

      if (!Array.isArray(data.playlist) || data.playlist.length === 0) {
        throw new Error("Este percurso não retornou músicas.");
      }

      const queue = data.playlist.filter((item) => item.preview_url).map((item) => ({
          id: item.track_id,
          title: item.nome,
          artist: item.artista,
          time: "0:30",
          image: item.cover_url || "https://via.placeholder.com/60",
          preview_url: item.preview_url,
      }));
      if (queue.length === 0) {
        throw new Error("Este percurso não possui músicas com prévia disponível.");
      }

      onPlay(queue[0], queue);
      setPage("now-playing");
    } catch (err) {
      setMixError(err instanceof Error ? err.message : "Falha ao gerar o percurso.");
    } finally {
      setGeneratingMixTitle("");
    }
  };

  return (
    <>
      {searchOpen && (
        <section className="home-search" aria-label="Buscar músicas">
          <label className="search-box home-search-box">
            <Search size={19} aria-hidden="true" />
            <input
              value={searchQuery}
              onChange={handleSearchQueryChange}
              placeholder="Buscar por música ou artista"
              aria-label="Buscar por música ou artista"
              autoFocus
            />
            <button
              className="search-close"
              type="button"
              onClick={onToggleSearch}
              aria-label="Fechar busca"
            >
              <X size={18} />
            </button>
          </label>

          {searchQuery.trim().length >= 2 && (
            <div className="search-results" aria-live="polite">
              {isSearching && <p className="search-feedback">Buscando músicas...</p>}
              {searchError && <p className="search-feedback" role="alert">{searchError}</p>}
              {!isSearching && !searchError && searchResults.length === 0 && (
                <p className="search-feedback">Nenhuma música foi encontrada.</p>
              )}
              {searchResults.length > 0 && (
                <p className="search-feedback">
                  {searchResults.length} de {searchTotal} músicas encontradas
                </p>
              )}
              {searchResults.map((track) => {
                const normalizedTrack = normalizeTrack(track);
                const isSelecting = selectingTrackId === normalizedTrack.id;
                return (
                  <button
                    className="search-result"
                    key={normalizedTrack.id}
                    type="button"
                    onClick={() => handleSearchTrackPlay(track)}
                    disabled={Boolean(selectingTrackId)}
                  >
                    <span className="search-result-info">
                      <strong>{normalizedTrack.title}</strong>
                      <small>{normalizedTrack.artist}</small>
                    </span>
                    <span className="search-result-action">
                      {isSelecting ? "Carregando..." : <Play size={16} fill="currentColor" />}
                    </span>
                  </button>
                );
              })}
              {searchResults.length < searchTotal && (
                <button
                  className="search-load-more"
                  type="button"
                  onClick={handleLoadMoreSearchResults}
                  disabled={isLoadingMore}
                >
                  {isLoadingMore ? "Carregando..." : "Carregar mais músicas"}
                </button>
              )}
            </div>
          )}
        </section>
      )}

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
              onClick={() => handleMixClick(mix)}
              disabled={Boolean(generatingMixTitle)}
              aria-busy={generatingMixTitle === mix.title}
            >
              <div className="mix-art">
                <img src={mix.image} alt="" />
                <span className="mix-index">0{index + 1}</span>
                <span className="card-play"><Play size={20} fill="currentColor" /></span>
              </div>
              <strong>{mix.title}</strong>
              <span>{generatingMixTitle === mix.title ? "A calcular rota..." : mix.subtitle}</span>
            </button>
          ))}
        </div>
        {mixError && <p role="alert">{mixError}</p>}
      </section>

      <section className="content-section tracks-section">
        <div className="section-heading">
          <div><span className="section-kicker">TOQUE E DESCUBRA</span><h2>Em alta</h2></div>
          <button className="text-button" onClick={onToggleSearch}>Explorar músicas <ChevronRight size={16} /></button>
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
                liked={likedIds.some((id) => String(id) === String(track.id ?? track.track_id))}
                onLike={onLike}
              />
            ))
          )}
        </div>
      </section>
    </>
  );
}