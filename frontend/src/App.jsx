import { useEffect, useState } from "react";
import { Search } from "lucide-react";
import "./App.css";

import Sidebar from "./components/Sidebar";
import Player from "./components/Player";

import HomePage from "./pages/HomePage";
import LibraryPage from "./pages/LibraryPage";
import PlaylistPage from "./pages/PlaylistPage";
import JourneyPage from "./pages/JourneyPage";
import NowPlayingPage from "./pages/NowPlayingPage";

import { tracks as defaultTracks } from "./data/tracks";

export default function App() {
  const [page, setPage] = useState("home");
  const [searchOpen, setSearchOpen] = useState(false);
  const [current, setCurrent] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [suggestionMessage, setSuggestionMessage] = useState("");
  const [likedTracks, setLikedTracks] = useState(() => {
    try {
      const savedTracks = JSON.parse(localStorage.getItem("vibestream-liked-tracks") || "[]");
      return Array.isArray(savedTracks) ? savedTracks : [];
    } catch (error) {
      console.error("Não foi possível carregar as músicas curtidas:", error);
      return [];
    }
  });
  const likedIds = likedTracks.map((track) => String(track.id ?? track.track_id));
  const [queue, setQueue] = useState(defaultTracks);
  const [queueMode, setQueueMode] = useState("default");

  useEffect(() => {
    try {
      localStorage.setItem("vibestream-liked-tracks", JSON.stringify(likedTracks));
    } catch (error) {
      console.error("Não foi possível salvar as músicas curtidas:", error);
    }
  }, [likedTracks]);

  const playTrack = (track, newQueue = null) => {
    if (!track) return;
    if (newQueue) setQueue(newQueue);
    setQueueMode("default");
    setCurrent(track);
    setIsPlaying(true);
    setSuggestionMessage("");
  };

  const openSearch = () => {
    setPage("home");
    setSearchOpen(true);
  };

  const toggleSearch = () => {
    if (page !== "home") {
      openSearch();
      return;
    }
    setSearchOpen((isOpen) => !isOpen);
  };

  const playSearchResult = (track, recommendations, message = "") => {
    if (!track?.preview_url) return;
    const trackId = String(track.id ?? track.track_id);
    const resolvedCover = track.image || track.cover_url;
    if (resolvedCover && !resolvedCover.includes("placeholder")) {
      setLikedTracks((savedTracks) => savedTracks.map((savedTrack) => (
        String(savedTrack.id ?? savedTrack.track_id) === trackId
          ? { ...savedTrack, image: resolvedCover, cover_url: resolvedCover }
          : savedTrack
      )));
    }
    const playableRecommendations = recommendations.filter(
      (item) => item.preview_url && !likedIds.includes(String(item.id ?? item.track_id))
    );
    setQueue([track, ...playableRecommendations]);
    setQueueMode("default");
    setCurrent(track);
    setIsPlaying(true);
    setSuggestionMessage(
      message || (!playableRecommendations.length ? "Não encontramos músicas próximas com prévia disponível." : "")
    );
    setSearchOpen(false);
    setPage("now-playing");
  };

  const playJourneyPlaylist = (playlist) => {
    if (!playlist || playlist.length === 0) return;
    const formattedQueue = playlist
      .filter((item) => item.preview_url && !likedIds.includes(String(item.track_id)))
      .map((item) => ({
        id: item.track_id,
        title: item.nome,
        artist: item.artista,
        time: "0:30",
        image: item.cover_url || "https://via.placeholder.com/60",
        preview_url: item.preview_url,
      }));
    if (formattedQueue.length === 0) return;
    setQueue(formattedQueue);
    setQueueMode("default");
    setCurrent(formattedQueue[0]);
    setIsPlaying(true);
    setSuggestionMessage("");
    setPage("now-playing");
  };

  const toggleLike = (track) => {
    const trackId = String(typeof track === "object" ? track.id ?? track.track_id : track);
    if (!trackId || trackId === "undefined") return;
    setLikedTracks((savedTracks) => {
      const alreadyLiked = savedTracks.some(
        (savedTrack) => String(savedTrack.id ?? savedTrack.track_id) === trackId
      );
      if (alreadyLiked) {
        return savedTracks.filter(
          (savedTrack) => String(savedTrack.id ?? savedTrack.track_id) !== trackId
        );
      }
      if (typeof track !== "object" || !track) return savedTracks;
      return [...savedTracks, { ...track, id: trackId, track_id: trackId }];
    });
  };

  const playLikedTrack = (track) => {
    const selectedTrackId = String(track.id ?? track.track_id);
    const likedQueue = [...likedTracks].reverse().filter(
      (item) => item.preview_url || String(item.id ?? item.track_id) === selectedTrackId
    );
    const selectedIndex = likedQueue.findIndex(
      (item) => String(item.id ?? item.track_id) === selectedTrackId
    );
    const queueFromSelection = selectedIndex < 0
      ? [track, ...likedQueue]
      : [...likedQueue.slice(selectedIndex), ...likedQueue.slice(0, selectedIndex)];
    setQueue(queueFromSelection);
    setQueueMode("liked");
    setCurrent(track);
    setIsPlaying(true);
    setSuggestionMessage("");
    setPage("now-playing");
  };

  const playQueuedTrack = (track) => {
    setCurrent(track);
    setIsPlaying(true);
    setSuggestionMessage("");
  };

  const stepTrack = (direction) => {
    if (!queue.length) return;
    const index = queue.findIndex(
      (track) => String(track.id ?? track.track_id) === String(current?.id ?? current?.track_id)
    );
    const nextIndex = index + direction;
    if (nextIndex >= 0 && nextIndex < queue.length) {
      setCurrent(queue[nextIndex]);
      setIsPlaying(true);
    } else if (queueMode === "liked" && queue.length > 0) {
      setCurrent(queue[(nextIndex + queue.length) % queue.length]);
      setIsPlaying(true);
    } else {
      setIsPlaying(false);
    }
  };

  return (
    <div className="app-shell">
      <Sidebar
        page={page}
        setPage={setPage}
        likedCount={likedIds.length}
        onOpenSearch={openSearch}
      />

      <main className="main-area">
        <header className="topbar">
          <div className="topbar-right">
            <button
              className={`topbar-search-toggle${searchOpen ? " active" : ""}`}
              onClick={toggleSearch}
              aria-label={searchOpen ? "Fechar busca" : "Buscar músicas"}
              aria-expanded={searchOpen}
            >
              <Search size={19} />
            </button>
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
              onSearchPlay={playSearchResult}
              searchOpen={searchOpen}
              onToggleSearch={toggleSearch}
              likedIds={likedIds}
              onLike={toggleLike}
              setPage={setPage}
            />
          )}

          {page === "journey" && (
            <JourneyPage onPlayPlaylist={playJourneyPlaylist} />
          )}

          {(page === "library" || page === "liked") && (
            <LibraryPage
              likedTracks={likedTracks}
              current={current}
              isPlaying={isPlaying}
              onPlay={playLikedTrack}
              onLike={toggleLike}
            />
          )}

          {page === "playlist" && <PlaylistPage />}

          {page === "now-playing" && (
            <NowPlayingPage
              current={current}
              queue={queue}
              onPlay={playQueuedTrack}
              likedIds={likedIds}
              showLikedQueueSuggestions={queueMode === "liked"}
              onLike={toggleLike}
              suggestionMessage={suggestionMessage}
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
        liked={current ? likedIds.includes(String(current.id ?? current.track_id)) : false}
        onLike={toggleLike}
      />
    </div>
  );
}