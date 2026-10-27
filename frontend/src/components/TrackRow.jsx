import { Heart, Play, MoreHorizontal } from "lucide-react";

export default function TrackRow({
  track,
  index,
  current,
  isPlaying,
  onPlay,
  liked,
  onLike,
}) {
  return (
    <div
      className={`track-row ${
        current?.id === track.id ? "track-current" : ""
      }`}
      onDoubleClick={() => onPlay(track)}
      role="button"
      tabIndex={0}
      onKeyDown={(event) =>
        event.key === "Enter" && onPlay(track)
      }
    >
      <button
        className="track-number"
        onClick={() => onPlay(track)}
        aria-label={`Tocar ${track.title}`}
      >
        {current?.id === track.id && isPlaying ? (
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

      <img
        className="track-thumb"
        src={track.image}
        alt={`Capa de ${track.album}`}
      />

      <div className="track-title-cell">
        <strong>{track.title}</strong>
        <span>{track.artist}</span>
      </div>

      <span className="track-album">{track.album}</span>

      <button
        className={`like-button ${liked ? "liked" : ""}`}
        onClick={() => onLike(track.id)}
        aria-label={liked ? "Descurtir" : "Curtir"}
      >
        <Heart
          size={17}
          fill={liked ? "currentColor" : "none"}
        />
      </button>

      <span className="track-time">{track.time}</span>

      <button className="more-button" aria-label="Mais opções">
        <MoreHorizontal size={18} />
      </button>
    </div>
  );
}