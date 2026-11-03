import { useState, useRef, useEffect, useCallback } from "react";
import {
  Heart,
  ListMusic,
  Music2,
  Pause,
  Play,
  Repeat,
  Shuffle,
  SkipBack,
  SkipForward,
  Volume2,
  VolumeX,
} from "lucide-react";
import { obterPrevia } from "../services/musicaService";

export default function Player({
  current,
  isPlaying,
  setIsPlaying,
  onNext,
  onPrevious,
  liked,
  onLike,
}) {
  const [volume, setVolume] = useState(0.70);
  const [isMuted, setIsMuted] = useState(false);
  const [playbackTime, setPlaybackTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [playbackNotice, setPlaybackNotice] = useState({ trackKey: null, message: "" });
  const [previewLookup, setPreviewLookup] = useState(null);
  const audioRef = useRef(null);
  const volumeTrackRef = useRef(null);
  const previewRequestId = useRef(0);
  const previewRequestTrack = useRef(null);
  const fallbackRequestTrack = useRef(null);
  const previousVolumeRef = useRef(0.70);

  const trackKey = current
    ? String(current.id ?? current.track_id ?? `${current.title || current.nome}-${current.artist || current.artista}`)
    : null;
  const activeTrackKey = useRef(trackKey);
  activeTrackKey.current = trackKey;
  const trackPreviewLookup = previewLookup?.trackKey === trackKey ? previewLookup : null;
  const previewUrl = trackPreviewLookup?.status === "fallback"
    ? trackPreviewLookup.url
    : trackPreviewLookup?.status === "fallback-error"
      ? null
      : current?.preview_url || trackPreviewLookup?.url || null;

  useEffect(() => {
    setPlaybackTime(0);
    setDuration(0);
    if (audioRef.current) {
      audioRef.current.currentTime = 0;
    }
  }, [trackKey, previewUrl]);

  const updatePlaybackTime = () => {
    const audio = audioRef.current;
    if (audio && Number.isFinite(audio.currentTime)) {
      setPlaybackTime(audio.currentTime);
    }
  };

  const updateDuration = () => {
    const audio = audioRef.current;
    if (audio && Number.isFinite(audio.duration)) {
      setDuration(audio.duration);
    }
  };

  const seekTo = (event) => {
    const audio = audioRef.current;
    const newTime = Number(event.target.value);
    if (!audio || !Number.isFinite(newTime)) return;
    audio.currentTime = newTime;
    setPlaybackTime(newTime);
  };

  const formatTime = (time) => {
    if (!Number.isFinite(time) || time < 0) return "0:00";
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${String(seconds).padStart(2, "0")}`;
  };

  const handlePlaybackError = useCallback((error) => {
    const message = error?.name === "NotAllowedError"
      ? "Clique em reproduzir para iniciar a prévia."
      : "Não foi possível carregar a prévia desta faixa.";
    setPlaybackNotice({ trackKey, message });
    setIsPlaying(false);
    if (error?.name !== "NotAllowedError") {
      console.error("Erro ao reproduzir a prévia:", error);
    }
  }, [setIsPlaying, trackKey]);

  const handleAudioError = useCallback(() => {
    if (!current || !trackKey || activeTrackKey.current !== trackKey) return;
    setIsPlaying(false);

    if (fallbackRequestTrack.current === trackKey) {
      setPreviewLookup({ trackKey, url: null, status: "fallback-error" });
      setPlaybackNotice({ trackKey, message: "Não foi possível carregar a prévia desta faixa." });
      return;
    }

    const nome = current.title || current.nome;
    const artista = current.artist || current.artista;
    if (!nome || !artista) {
      setPlaybackNotice({ trackKey, message: "Não foi possível carregar a prévia desta faixa." });
      return;
    }

    fallbackRequestTrack.current = trackKey;
    const failedUrl = previewUrl;
    const requestId = ++previewRequestId.current;
    setPlaybackNotice({ trackKey, message: "Buscando outra prévia para esta faixa..." });
    obterPrevia(nome, artista)
      .then((url) => {
        if (requestId !== previewRequestId.current || activeTrackKey.current !== trackKey) return;
        if (url && url !== failedUrl) {
          setPreviewLookup({ trackKey, url, status: "fallback" });
          setPlaybackNotice({ trackKey, message: "" });
          setIsPlaying(true);
          return;
        }
        setPreviewLookup({ trackKey, url: null, status: "fallback-error" });
        setPlaybackNotice({ trackKey, message: "Prévia de áudio indisponível para esta faixa." });
      })
      .catch((error) => {
        if (requestId !== previewRequestId.current || activeTrackKey.current !== trackKey) return;
        console.error("Erro ao buscar uma prévia alternativa:", error);
        setPreviewLookup({ trackKey, url: null, status: "fallback-error" });
        setPlaybackNotice({
          trackKey,
          message: "Não foi possível buscar outra prévia. Tente novamente.",
        });
      });
  }, [current, previewUrl, setIsPlaying, trackKey]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    if (!isPlaying) {
      audio.pause();
      return;
    }

    if (!previewUrl) {
      if (
        current &&
        previewLookup?.trackKey !== trackKey &&
        previewRequestTrack.current !== trackKey
      ) {
        const requestId = ++previewRequestId.current;
        const nome = current.title || current.nome;
        const artista = current.artist || current.artista;
        if (!nome || !artista) return;
        previewRequestTrack.current = trackKey;
        obterPrevia(nome, artista)
          .then((url) => {
            if (requestId !== previewRequestId.current) return;
            setPreviewLookup({ trackKey, url, status: url ? "found" : "missing" });
            setPlaybackNotice({
              trackKey,
              message: url ? "" : "Prévia de áudio indisponível para esta faixa.",
            });
            if (!url) setIsPlaying(false);
          })
          .catch((error) => {
            if (requestId !== previewRequestId.current) return;
            console.error("Erro ao buscar a prévia da faixa:", error);
            setPreviewLookup({ trackKey, url: null, status: "error" });
            setPlaybackNotice({
              trackKey,
              message: "Não foi possível buscar a prévia. Verifique a conexão com o servidor.",
            });
            setIsPlaying(false);
          });
      }
      return;
    }

    if (audio.paused) {
      audio.play().catch(handlePlaybackError);
    }
  }, [isPlaying, current, previewUrl, previewLookup, trackKey, handlePlaybackError, setIsPlaying]);

  const handlePlayClick = () => {
    const audio = audioRef.current;
    if (!current || !audio) return;
    if (!previewUrl) {
      if (previewRequestTrack.current === trackKey && previewLookup?.trackKey !== trackKey) {
        setPlaybackNotice({ trackKey, message: "Buscando prévia da faixa..." });
        return;
      }
      if (
        previewLookup?.trackKey === trackKey &&
        ["error", "missing", "fallback-error"].includes(previewLookup.status)
      ) {
        fallbackRequestTrack.current = null;
        previewRequestTrack.current = null;
        setPreviewLookup(null);
        setPlaybackNotice({ trackKey, message: "Buscando prévia da faixa..." });
        setIsPlaying(true);
        return;
      }
      setPlaybackNotice({ trackKey, message: "Prévia de áudio indisponível para esta faixa." });
      return;
    }

    setPlaybackNotice({ trackKey, message: "" });
    audio.play()
      .then(() => setIsPlaying(true))
      .catch(handlePlaybackError);
  };

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = volume;
      audioRef.current.muted = isMuted;
    }
  }, [volume, isMuted]);

  const handleVolumeChange = (e) => {
    if (!volumeTrackRef.current) return;
    const rect = volumeTrackRef.current.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    let newVolume = clickX / rect.width;
    newVolume = Math.max(0, Math.min(1, newVolume));
    setVolume(newVolume);
    if (newVolume > 0) {
      previousVolumeRef.current = newVolume;
      setIsMuted(false);
    }
  };

  const toggleMute = () => {
    if (isMuted) {
      setVolume(previousVolumeRef.current || 0.70);
      setIsMuted(false);
      return;
    }
    if (volume > 0) previousVolumeRef.current = volume;
    setIsMuted(true);
  };

  const handleMouseDown = (e) => {
    handleVolumeChange(e);
    const handleMouseMove = (e) => handleVolumeChange(e);
    const handleMouseUp = () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);
  };

  const currentImage = current?.image || current?.cover_url;
  const hasValidImage = currentImage && !currentImage.includes("placeholder") && currentImage !== "nan";
  const playbackMessage = playbackNotice.trackKey === trackKey ? playbackNotice.message : "";

  console.log("Dados da música no Player:", current);
  
  return (
    <footer className="player">
      <audio 
        ref={audioRef} 
        src={previewUrl || undefined}
        onEnded={onNext}
        onError={handleAudioError}
        onTimeUpdate={updatePlaybackTime}
        onLoadedMetadata={updateDuration}
        onDurationChange={updateDuration}
      />

      <div className="player-track">
        {hasValidImage ? (
          <img
            src={currentImage}
            alt=""
            className="player-cover"
          />
        ) : (
          <div className="player-cover empty-cover" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#222', borderRadius: '4px', width: '56px', height: '56px', flexShrink: 0 }}>
            <Music2 size={24} color="#888" />
          </div>
        )}

        <div className="player-song">
          <strong>{current?.title || current?.nome || "Escolha uma música"}</strong>
          <span aria-live="polite">
            {playbackMessage || current?.artist || current?.artista || "Sua próxima vibe começa aqui"}
          </span>
        </div>

        {current && (
          <button
            className={`like-button player-like ${liked ? "liked" : ""}`}
            onClick={() => onLike(current)}
            aria-label={liked ? "Descurtir música" : "Curtir música"}
          >
            <Heart size={17} fill={liked ? "currentColor" : "none"} />
          </button>
        )}
      </div>

      <div className="player-center">
        <div className="player-controls">
          <button className="control-button optional-control" aria-label="Aleatório">
            <Shuffle size={17} />
          </button>

          <button className="control-button" onClick={onPrevious} aria-label="Música anterior">
            <SkipBack size={20} fill="currentColor" />
          </button>

          <button
            className="play-main"
            onClick={() => {
              if (isPlaying) {
                setIsPlaying(false);
                return;
              }
              handlePlayClick();
            }}
            aria-label={isPlaying ? "Pausar" : "Tocar"}
          >
            {isPlaying ? <Pause size={20} fill="currentColor" /> : <Play size={20} fill="currentColor" />}
          </button>

          <button className="control-button" onClick={onNext} aria-label="Próxima música">
            <SkipForward size={20} fill="currentColor" />
          </button>

          <button className="control-button optional-control" aria-label="Repetir">
            <Repeat size={17} />
          </button>
        </div>

        <div className="progress-row">
          <span>{formatTime(playbackTime)}</span>
          <input
            className="progress-slider"
            type="range"
            min="0"
            max={duration || 0}
            step="0.1"
            value={Math.min(playbackTime, duration || 0)}
            onChange={seekTo}
            disabled={!duration}
            aria-label="Posição da faixa"
            style={{
              "--progress": `${duration ? (playbackTime / duration) * 100 : 0}%`,
            }}
          />
          <span>{duration ? formatTime(duration) : current?.time || "0:30"}</span>
        </div>
      </div>

      <div className="player-volume">
        <ListMusic size={18} />
        <button
          className="volume-mute-button"
          type="button"
          onClick={toggleMute}
          aria-label={isMuted ? "Ativar som" : "Silenciar"}
          aria-pressed={isMuted}
          title={isMuted ? "Ativar som" : "Silenciar"}
        >
          {isMuted || volume === 0 ? <VolumeX size={19} /> : <Volume2 size={19} />}
        </button>
        <div 
          className="volume-track" 
          ref={volumeTrackRef} 
          onMouseDown={handleMouseDown} 
          role="slider"
          aria-label="Volume"
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={Math.round(volume * 100)}
          tabIndex={0}
          onKeyDown={(event) => {
            if (event.key === "ArrowLeft" || event.key === "ArrowDown") {
              event.preventDefault();
              setVolume((currentVolume) => Math.max(0, currentVolume - 0.05));
              setIsMuted(false);
            } else if (event.key === "ArrowRight" || event.key === "ArrowUp") {
              event.preventDefault();
              setVolume((currentVolume) => Math.min(1, currentVolume + 0.05));
              setIsMuted(false);
            }
          }}
          title={`Volume: ${Math.round(volume * 100)}%`}
        >
          <div className="volume-fill" style={{ width: `${isMuted ? 0 : volume * 100}%` }} />
        </div>
      </div>
    </footer>
  );
}