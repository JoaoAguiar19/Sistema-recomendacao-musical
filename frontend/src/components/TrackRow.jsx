import { Heart, Play, MoreHorizontal, Music2 } from "lucide-react";

export default function TrackRow({
  track,
  index,
  current,
  isPlaying,
  onPlay,
  liked,
  onLike,
}) {
  const trackId = track.id || track.track_id;
  const isCurrent = (current?.id || current?.track_id) === trackId;
  const trackImage = track.image || track.cover_url;

  return (
    <div
      className={`track-row ${isCurrent ? "track-current" : ""}`}
      onDoubleClick={() => onPlay(track)}
      role="button"
      tabIndex={0}
      onKeyDown={(event) => event.key === "Enter" && onPlay(track)}
    >
      <button
        className="track-number"
        onClick={(e) => {
          e.stopPropagation();
          onPlay(track);
        }}
        aria-label={`Tocar ${track.title || track.nome}`}
      >
        {isCurrent && isPlaying ? (
          <span className="equalizer">▮▮▮</span>
        ) : (
          <>
            <span className="number">
              {String(index + 1).padStart(2, "0")}
            </span>
            <Play size={15} className="number-play" />
          </>
        )}
      </button>

      {trackImage && trackImage !== "nan" && !trackImage.includes("placeholder") ? (
        <img
          className="track-thumb"
          src={trackImage}
          alt={`Capa de ${track.title || track.nome}`}
        />
      ) : (
        <div className="track-thumb empty-thumb" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#222', borderRadius: '4px', width: '40px', height: '40px' }}>
          <Music2 size={18} color="#888" />
        </div>
      )}

      <div className="track-title-cell">
        <strong>{track.title || track.nome}</strong>
        <span>{track.artist || track.artista}</span>
      </div>

      <span className="track-album">{track.album || "VibeStream Mix"}</span>

      <button
        className={`like-button ${liked ? "liked" : ""}`}
        onClick={(e) => {
          e.stopPropagation();
          onLike(trackId);
        }}
        aria-label={liked ? "Descurtir" : "Curtir"}
      >
        <Heart size={17} fill={liked ? "currentColor" : "none"} />
      </button>

      <span className="track-time">{track.time || "0:30"}</span>

      <button 
        className="more-button" 
        aria-label="Mais opções"
        onClick={(e) => e.stopPropagation()}
      >
        <MoreHorizontal size= {18} />
      </button>
    </div>
  );
}