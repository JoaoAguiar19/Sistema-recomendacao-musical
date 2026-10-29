import { useState, useRef } from "react";
import { ArrowRight, Music2, Route, Search } from "lucide-react";
import "./JourneyPage.css";

function BuscaMusica({ label, valor, setValor, placeholder }) {
  const [busca, setBusca] = useState("");
  const [aberto, setAberto] = useState(false);
  const [resultados, setResultados] = useState([]);
  const [carregandoBusca, setCarregandoBusca] = useState(false);
  const debounceRef = useRef(null);

  const handleDigitacao = (e) => {
    const termo = e.target.value;
    setBusca(termo);
    setAberto(true);
    
    // Se o utilizador voltar a digitar, limpa o ID selecionado
    if (valor) setValor(""); 

    if (debounceRef.current) clearTimeout(debounceRef.current);

    if (termo.length < 2) {
      setResultados([]);
      setCarregandoBusca(false);
      return;
    }

    setCarregandoBusca(true);
    
    // Debounce de 400ms para aguardar o utilizador parar de digitar
    debounceRef.current = setTimeout(async () => {
      try {
        const resposta = await fetch(`http://127.0.0.1:8000/musicas?busca=${encodeURIComponent(termo)}&limite=15`);
        if (resposta.ok) {
          const dados = await resposta.json();
          setResultados(dados.musicas || []);
        }
      } catch (erro) {
        console.error("Erro na busca", erro);
      } finally {
        setCarregandoBusca(false);
      }
    }, 400);
  };

  return (
    <label>
      <span>{label}</span>
      <div style={{ position: "relative", width: "100%" }}>
        <input
          type="text"
          placeholder={placeholder}
          value={busca}
          onChange={handleDigitacao}
          onFocus={() => {
            if (busca.length >= 2) setAberto(true);
          }}
          onBlur={() => setTimeout(() => setAberto(false), 200)}
          style={{
            width: "100%", minHeight: "54px", padding: "0 16px", color: "#f4f5ff",
            backgroundColor: "#0a1020", border: "1px solid #303a5a", borderRadius: "12px",
            font: "inherit", fontSize: "14px", outline: "none", transition: "border-color 0.2s"
          }}
        />
        
        {aberto && busca.length >= 2 && (
          <ul style={{
            position: "absolute", top: "calc(100% + 5px)", left: 0, right: 0, backgroundColor: "#10172a",
            maxHeight: "250px", overflowY: "auto", listStyle: "none", padding: 0, margin: 0,
            borderRadius: "12px", border: "1px solid #303a5a", zIndex: 10, boxShadow: "0 4px 20px rgba(4, 9, 29, 0.9)"
          }}>
            {carregandoBusca ? (
              <li style={{ padding: "14px", textAlign: "center", color: "#a7aec5" }}>A procurar no catálogo...</li>
            ) : resultados.length === 0 ? (
              <li style={{ padding: "14px", textAlign: "center", color: "#a7aec5" }}>Nenhuma faixa encontrada.</li>
            ) : (
              resultados.map((m) => (
                <li
                  key={m.track_id}
                  onClick={() => {
                    setValor(m.track_id);
                    setBusca(`${m.nome} — ${m.artista}`);
                    setAberto(false);
                  }}
                  style={{ padding: "12px 16px", cursor: "pointer", borderBottom: "1px solid #252e49", color: "#f4f5ff" }}
                  onMouseOver={(e) => e.currentTarget.style.backgroundColor = "#202a48"}
                  onMouseOut={(e) => e.currentTarget.style.backgroundColor = "transparent"}
                >
                  <strong>{m.nome}</strong> <span style={{ color: "#a7aec5", fontSize: "13px" }}>— {m.artista}</span>
                  {!m.no_grafo && (
                    <span style={{ marginLeft: "8px", fontSize: "10px", backgroundColor: "#303a5a", padding: "2px 6px", borderRadius: "4px" }}>
                      Busca Expandida
                    </span>
                  )}
                </li>
              ))
            )}
          </ul>
        )}
      </div>
    </label>
  );
}

export default function JourneyPage({ onPlayPlaylist }) {
  const [musicaInicial, setMusicaInicial] = useState("");
  const [musicaFinal, setMusicaFinal] = useState("");
  const [mensagem, setMensagem] = useState("");
  const [percurso, setPercurso] = useState([]);
  const [carregando, setCarregando] = useState(false);

  const iniciarPercurso = async () => {
    if (!musicaInicial || !musicaFinal) {
      setMensagem("Escolha as duas músicas a partir da lista para continuar.");
      return;
    }
    if (musicaInicial === musicaFinal) {
      setMensagem("Escolha duas músicas diferentes.");
      return;
    }

    setMensagem("");
    setPercurso([]);
    setCarregando(true);

    try {
      const resposta = await fetch("http://127.0.0.1:8000/recomendar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ origem_id: musicaInicial, destino_id: musicaFinal }),
      });

      if (!resposta.ok) {
        const erroData = await resposta.json();
        throw new Error(erroData.detail || "Erro na resposta do servidor");
      }

      const dados = await resposta.json();
      const playlist = dados.playlist || [];
      setPercurso(playlist);

      // Envia a playlist para o App.jsx iniciar a reprodução automática no player global
      if (onPlayPlaylist && playlist.length > 0) {
        onPlayPlaylist(playlist);
      }
    } catch (erro) {
      setMensagem(typeof erro.message === "string" ? erro.message : "Falha ao calcular o percurso.");
    } finally {
      setCarregando(false);
    }
  };

  return (
    <section className="journey-page">
      <div className="journey-heading">
        <span className="journey-label"><Route size={16} /> PERCURSO MUSICAL</span>
        <h1>De uma música a outra.</h1>
        <p>Escolha onde começar e onde quer chegar. Encontre um caminho musical com transições graduais.</p>
      </div>

      <div className="journey-form">
        <BuscaMusica 
          label="01 — Música inicial (A)" 
          placeholder="Digite o nome ou artista..." 
          valor={musicaInicial} 
          setValor={setMusicaInicial} 
        />

        <div className="journey-connector">
          <div /><ArrowRight size={20} /><div />
        </div>

        <BuscaMusica 
          label="02 — Música final (B)" 
          placeholder="Digite o nome ou artista..." 
          valor={musicaFinal} 
          setValor={setMusicaFinal} 
        />

        <button className="journey-button" onClick={iniciarPercurso} disabled={carregando}>
          <Search size={18} />
          {carregando ? "Calculando caminho..." : "Encontrar meu caminho"}
        </button>

        {mensagem && <p className="journey-message" role="status">{mensagem}</p>}
      </div>

      {percurso.length > 0 && (
        <div className="journey-result">
          <h2>Seu Percurso Musical ({percurso.length} faixas)</h2>
          <div className="journey-playlist">
            {percurso.map((item) => (
              <div key={item.track_id} className="journey-embed-card">
                <iframe
                  title={`Spotify Player - ${item.nome}`}
                  src={`https://open.spotify.com/embed/track/${item.track_id}?utm_source=generator&theme=0`}
                  width="100%"
                  height="80"
                  frameBorder="0"
                  allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
                  loading="lazy"
                />
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="journey-info">
        <div className="journey-info-icon"><Music2 size={22} /></div>
        <div>
          <h2>Uma música de cada vez</h2>
          <p>A proposta é conectar as músicas escolhidas por meio de faixas intermediárias semelhantes, evitando mudanças bruscas de ritmo.</p>
        </div>
      </div>
    </section>
  );
}