
import {
  Home,
  Search,
  Library,
  Heart,
  Plus,
  Compass,
  Radio,
  MoreHorizontal,
  Music2,
  Route,
} from "lucide-react";

export default function Sidebar({ page, setPage, likedCount }) {
  return (
    <aside className="sidebar">
      <button
        className="brand"
        onClick={() => setPage("home")}
        aria-label="Ir para início"
      >
        <span className="brand-mark">
          <Music2 size={22} />
        </span>

        <span>
          Vibe<span className="brand-light">Stream</span>
        </span>
      </button>

      <nav className="nav-group" aria-label="Navegação principal">
        <button
          className={page === "home" ? "nav-item active" : "nav-item"}
          onClick={() => setPage("home")}
        >
          <Home size={19} /> Início
        </button>

        <button
          className={page === "search" ? "nav-item active" : "nav-item"}
          onClick={() => setPage("search")}
        >
          <Search size={19} /> Buscar
        </button>

        <button
          className={page === "journey" ? "nav-item active" : "nav-item"}
          onClick={() => setPage("journey")}
        >
          <Route size={19} /> Percurso musical
        </button>

        <button
          className={page === "library" ? "nav-item active" : "nav-item"}
          onClick={() => setPage("library")}
        >
          <Library size={19} /> Sua biblioteca
        </button>
      </nav>

      <div className="sidebar-divider" />

      <p className="side-label">SUA COLEÇÃO</p>

      <button className="nav-item" onClick={() => setPage("library")}>
        <Plus size={19} /> Criar playlist
      </button>

      <button
        className={page === "liked" ? "nav-item active" : "nav-item"}
        onClick={() => setPage("liked")}
      >
        <Heart size={19} />
        Músicas curtidas
        <span className="nav-count">{likedCount}</span>
      </button>

      <div className="sidebar-divider" />

      <p className="side-label">EXPLORAR</p>

      <button className="nav-item" onClick={() => setPage("search")}>
        <Compass size={19} /> Descobrir
      </button>

      <button className="nav-item" onClick={() => setPage("search")}>
        <Radio size={19} /> Rádios
      </button>

      <div className="sidebar-bottom">
        <div className="upgrade-card">
          <span className="upgrade-icon">
            <Music2 size={18} />
          </span>

          <div>
            <strong>Sua vibe, sem limites</strong>
            <p>Descubra novos sons todos os dias.</p>
          </div>
        </div>

        <div className="profile">
          <div className="avatar">C</div>

          <div>
            <strong>Olá, ouvinte</strong>
            <span>Conta gratuita</span>
          </div>

          <MoreHorizontal size={20} className="muted-icon" />
        </div>
      </div>
    </aside>
  );
}
