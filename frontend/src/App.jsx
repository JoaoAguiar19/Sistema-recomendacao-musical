import { useState } from "react";
import "./App.css";

import Sidebar from "./components/Sidebar";
import Player from "./components/Player";

import HomePage from "./pages/HomePage";
import SearchPage from "./pages/SearchPage";
import LibraryPage from "./pages/LibraryPage";
import JourneyPage from "./pages/JourneyPage";
import NowPlayingPage from "./pages/NowPlayingPage";

import { tracks as defaultTracks } from "./data/tracks";

export default function App() {
  const [page, setPage] = useState("home");
  const [current, setCurrent] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [likedIds, setLikedIds] = useState([3]);
  const [queue, setQueue] = useState(defaultTracks);

  const playTrack = (track, newQueue = null) => {
    if (!track) return;
    if (newQueue) setQueue(newQueue);
    setCurrent(track);
    setIsPlaying(true);
  };

  const playJourneyPlaylist = (playlist) => {
    if (!playlist || playlist.length === 0) return;
    const formattedQueue = playlist.map((item) => ({
      id: item.track_id,
      title: item.nome,
      artist: item.artista,
      time: "0:30",
      image: item.cover_url || "https://via.placeholder.com/60",
      preview_url: item.preview_url,
    }));
    setQueue(formattedQueue);
    setCurrent(formattedQueue[0]);
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
    if (!queue.length) return;
    const index = queue.findIndex(
      (track) => (track.id || track.track_id) === (current?.id || current?.track_id)
    );
    const nextIndex = index + direction;
    if (nextIndex >= 0 && nextIndex < queue.length) {
      setCurrent(queue[nextIndex]);
      setIsPlaying(true);
    } else {
      setIsPlaying(false);
    }
  };

  return (
    <div className="app-shell">
      <Sidebar page={page} setPage={setPage} likedCount={likedIds.length} />

      <main className="main-area">
        <header className="topbar">
          <div className="topbar-right">
            <span className="status-pill"><span /> SUA MÚSICA, SEU ESTILO</span>
            <button className="profile-small">C</button>
          </div>
        </header>

        <div className={`page-scroll${page === "now-playing" ? " now-playing-scroll" : ""}`}>
          {page === "home" && (
            <HomePage
              current={current}
              isPlaying={isPlaying}
              onPlay={(t, customQueue) => playTrack(t, customQueue || defaultTracks)}
              likedIds={likedIds}
              onLike={toggleLike}
              setPage={setPage}
            />
          )}

          {page === "search" && (
            <SearchPage onPlay={(t) => playTrack(t, defaultTracks)} likedIds={likedIds} onLike={toggleLike} />
          )}

          {page === "journey" && (
            <JourneyPage onPlayPlaylist={playJourneyPlaylist} />
          )}

          {(page === "library" || page === "liked") && (
            <LibraryPage likedIds={likedIds} onPlay={(t) => playTrack(t, defaultTracks)} onLike={toggleLike} />
          )}

          {page === "now-playing" && (
            <NowPlayingPage
              current={current}
              queue={queue}
              onPlay={(t) => playTrack(t, queue)}
              likedIds={likedIds}
              onLike={toggleLike}
              setPage={setPage} 
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
        liked={current ? likedIds.includes(current.id || current.track_id) : false}
        onLike={toggleLike}
      />
    </div>
  );
}