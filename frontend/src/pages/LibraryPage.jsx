import { Heart } from "lucide-react";

import TrackRow from "../components/TrackRow";
import { tracks } from "../data/tracks";

export default function LibraryPage({ likedIds, onPlay }) {
  const liked = tracks.filter((track) =>
    likedIds.includes(track.id)
  );

  return (
    <section className="simple-page">
      <span className="section-kicker">SEU ESPAÇO MUSICAL</span>

      <h1>Sua biblioteca</h1>

      <p className="page-description">
        Tudo o que você guardar fica reunido aqui.
      </p>

      <div className="library-feature">
        <div className="library-heart">
          <Heart size={32} fill="currentColor" />
        </div>

        <div>
          <span>PLAYLIST</span>
          <h2>Músicas curtidas</h2>

          <p>
            {liked.length}{" "}
            {liked.length === 1
              ? "música salva"
              : "músicas salvas"}
          </p>
        </div>
      </div>

      {liked.length ? (
        liked.map((track, index) => (
          <TrackRow
            key={track.id}
            track={track}
            index={index}
            current={null}
            isPlaying={false}
            onPlay={onPlay}
            liked
            onLike={() => {}}
          />
        ))
      ) : (
        <div className="empty-state">
          Você ainda não curtiu nenhuma música. Use o coração ao lado
          de uma faixa para salvá-la aqui.
        </div>
      )}
    </section>
  );
}