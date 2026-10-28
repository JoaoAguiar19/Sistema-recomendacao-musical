import { useState } from "react";
import { Search } from "lucide-react";

import TrackRow from "../components/TrackRow";
import { tracks } from "../data/tracks";

export default function SearchPage({ onPlay, likedIds = [], onLike }) {
  const [query, setQuery] = useState("");

  const filtered = tracks.filter((track) =>
    `${track.title} ${track.artist} ${track.album}`
      .toLowerCase()
      .includes(query.toLowerCase())
  );

  return (
    <section className="simple-page">
      <span className="section-kicker">EXPLORE NOVOS SONS</span>

      <h1>Buscar músicas</h1>

      <p className="page-description">
        Encontre uma faixa, artista ou álbum para combinar com seu momento.
      </p>

      {/*{searchTerm && (
        <h2 className="search-results-title">
          Resultados para "{searchTerm}"
        </h2>
      )}*/}

      <label className="search-box">
        <Search size={20} />

        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="O que você quer ouvir?"
          autoFocus
        />
      </label>

      <h2 className="search-results-title">
        {query ? `Resultados para “${query}”` : "Sugestões para você"}
      </h2>

      {filtered.length ? (
        filtered.map((track, index) => (
          <TrackRow
            key={track.id}
            track={track}
            index={index}
            current={null}
            isPlaying={false}
            onPlay={onPlay}
            liked={likedIds.includes(track.id)}
            onLike={() => onLike(track.id)}
          />
        ))
      ) : (
        <p className="empty-state">
          Nenhuma música encontrada. Tente outro termo.
        </p>
      )}
    </section>
  );
}