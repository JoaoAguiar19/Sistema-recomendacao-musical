
import { useState } from "react";
import "./App.css";

import Sidebar from "./components/Sidebar";
import Player from "./components/Player";

import HomePage from "./pages/HomePage";
import SearchPage from "./pages/SearchPage";
import LibraryPage from "./pages/LibraryPage";
import JourneyPage from "./pages/JourneyPage";

import { tracks } from "./data/tracks";

export default function App() {
  const [page, setPage] = useState("home");
  const [current, setCurrent] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [likedIds, setLikedIds] = useState([3]);

  const playTrack = (track) => {
    if (!track) return;

    setCurrent(track);
    setIsPlaying(true);
  };

  const toggleLike = (id) => {
    setLikedIds((ids) =>
      ids.includes(id)
        ? ids.filter((likedId) => likedId !== id)
        : [...ids, id]
    );
  };

  const stepTrack = (direction) => {
    if (!tracks.length) return;

    const index = tracks.findIndex(
      (track) => track.id === current?.id
    );

    const nextIndex =
      index < 0
        ? 0
        : (index + direction + tracks.length) % tracks.length;

    playTrack(tracks[nextIndex]);
  };

  return (
    <div className="app-shell">
      <Sidebar
        page={page}
        setPage={setPage}
        likedCount={likedIds.length}
      />

      <main className="main-area">
        <header className="topbar">

          <div className="topbar-right">
            <span className="status-pill">
              <span /> SUA MÚSICA, SEU ESTILO
            </span>

            <button className="profile-small">C</button>
          </div>
        </header>

        <div className="page-scroll">
          {page === "home" && (
            <HomePage
              current={current}
              isPlaying={isPlaying}
              onPlay={playTrack}
              likedIds={likedIds}
              onLike={toggleLike}
              setPage={setPage}
            />
          )}

          {page === "search" && (
            <SearchPage
              onPlay={playTrack}
              likedIds={likedIds}
              onLike={toggleLike}
            />
          )}

          {page === "journey" && <JourneyPage />}

          {(page === "library" || page === "liked") && (
            <LibraryPage
              likedIds={likedIds}
              onPlay={playTrack}
              onLike={toggleLike}
            />
          )}
        </div>
      </main>

      <Player
        current={current}
        isPlaying={isPlaying}
        setIsPlaying={setIsPlaying}
        onNext={() => stepTrack(1)}
        onPrevious={() => stepTrack(-1)}
        liked={current ? likedIds.includes(current.id) : false}
        onLike={toggleLike}
      />
    </div>
  );
}
