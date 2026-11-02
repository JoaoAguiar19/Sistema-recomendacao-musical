import { useState, useRef, useEffect } from "react";
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
} from "lucide-react";

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
  const audioRef = useRef(null);
  const volumeTrackRef = useRef(null);

  useEffect(() => {
    if (audioRef.current) {
      if (isPlaying) {
        if (current?.preview_url) {
          const playPromise = audioRef.current.play();
          if (playPromise !== undefined) {
            playPromise.catch((error) => {
              console.error("Erro ao tocar áudio (link quebrado ou bloqueio do navegador):", error);
              setIsPlaying(false);
            });
          }
        } else {
          // Se a música não tem áudio disponível, desativa o botão de play visualmente
          setIsPlaying(false);
        }
      } else {
        audioRef.current.pause();
      }
    }
  }, [isPlaying, current]);

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = volume;
    }
  }, [volume]);

  const handleVolumeChange = (e) => {
    if (!volumeTrackRef.current) return;
    const rect = volumeTrackRef.current.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    let newVolume = clickX / rect.width;
    newVolume = Math.max(0, Math.min(1, newVolume));
    setVolume(newVolume);
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

  console.log("Dados da música no Player:", current);
  
  return (
    <footer className="player">
      <audio 
        ref={audioRef} 
        src={current?.preview_url} 
        onEnded={onNext}
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
          <span>{current?.artist || current?.artista || "Sua próxima vibe começa aqui"}</span>
        </div>

        {current && (
          <button
            className={`like-button player-like ${liked ? "liked" : ""}`}
            onClick={() => onLike(current.id)}
            aria-label="Curtir música"
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
            onClick={() => current && setIsPlaying(!isPlaying)}
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
          <span>0:00</span>
          <div className="progress-track">
            <div className={isPlaying ? "progress-fill animated-progress" : "progress-fill"} />
          </div>
          <span>{current?.time || "0:30"}</span>
        </div>
      </div>

      <div className="player-volume">
        <ListMusic size={18} />
        <Volume2 size={19} />
        <div 
          className="volume-track" 
          ref={volumeTrackRef} 
          onMouseDown={handleMouseDown} 
          title={`Volume: ${Math.round(volume * 100)}%`}
        >
          <div className="volume-fill" style={{ width: `${volume * 100}%` }} />
        </div>
      </div>
    </footer>
  );
}