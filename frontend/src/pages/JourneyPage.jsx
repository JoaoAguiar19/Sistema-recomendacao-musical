import { useState, useRef, useEffect } from "react";
import { Activity, ArrowRight, Music2, Route, Search, SlidersHorizontal, Sparkles } from "lucide-react";
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
  const [perfis, setPerfis] = useState([]);
  const [perfilSelecionado, setPerfilSelecionado] = useState("");
  const [perfilGerado, setPerfilGerado] = useState(null);
  const [modoManual, setModoManual] = useState(false);
  const [musicaInicial, setMusicaInicial] = useState("");
  const [musicaFinal, setMusicaFinal] = useState("");
  const [mensagem, setMensagem] = useState("");
  const [percurso, setPercurso] = useState([]);
  const [carregando, setCarregando] = useState(false);

  useEffect(() => {
    const controller = new AbortController();

    fetch("http://127.0.0.1:8000/percursos", { signal: controller.signal })
      .then((resposta) => {
        if (!resposta.ok) throw new Error("Não foi possível carregar os caminhos disponíveis.");
        return resposta.json();
      })
      .then((dados) => {
        const caminhos = dados.percursos || [];
        setPerfis(caminhos);
        setPerfilSelecionado(caminhos[0]?.id || "");
      })
      .catch((erro) => {
        if (erro.name !== "AbortError") setMensagem(erro.message);
      });

    return () => controller.abort();
  }, []);

  const calcularPercurso = async (endpoint, dadosRequisicao) => {
    setMensagem("");
    setPercurso([]);
    setPerfilGerado(null);
    setCarregando(true);

    try {
      const resposta = await fetch(`http://127.0.0.1:8000${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(dadosRequisicao),
      });

      if (!resposta.ok) {
        const erroData = await resposta.json();
        throw new Error(erroData.detail || "Erro na resposta do servidor");
      }

      const dados = await resposta.json();
      const playlist = dados.playlist || [];
      setPercurso(playlist);
      setPerfilGerado(dados.perfil || null);

      if (onPlayPlaylist && playlist.length > 0) {
        onPlayPlaylist(playlist);
      }
    } catch (erro) {
      setMensagem(typeof erro.message === "string" ? erro.message : "Falha ao calcular o percurso.");
    } finally {
      setCarregando(false);
    }
  };

  const iniciarPercursoPredefinido = () => {
    if (!perfilSelecionado) {
      setMensagem("Escolha um caminho para continuar.");
      return;
    }
    calcularPercurso("/recomendar-percurso", { percurso_id: perfilSelecionado });
  };

  const iniciarPercurso = async () => {
    if (!musicaInicial || !musicaFinal) {
      setMensagem("Escolha as duas músicas a partir da lista para continuar.");
      return;
    }
    if (musicaInicial === musicaFinal) {
      setMensagem("Escolha duas músicas diferentes.");
      return;
    }

    calcularPercurso("/recomendar", {
      origem_id: musicaInicial,
      destino_id: musicaFinal,
    });
  };

  const perfilAtual = perfis.find((perfil) => perfil.id === perfilSelecionado);

  return (
    <section className="journey-page">
      <div className="journey-heading">
        <span className="journey-label"><Route size={16} /> PERCURSO MUSICAL</span>
        <h1>Conecte uma música à outra.</h1>
        <p>Escolha faixas de partida e chegada por BPM normalizado. O A* encontra a rota de menor custo considerando ritmo, energia, estilo, harmonia e popularidade.</p>
      </div>

      <div className="journey-form">
        <div className="journey-mode-switch" role="tablist" aria-label="Modo de criação do percurso">
          <button
            type="button"
            className={!modoManual ? "active" : ""}
            role="tab"
            aria-selected={!modoManual}
            onClick={() => setModoManual(false)}
          >
            <Sparkles size={16} /> Caminhos prontos
          </button>
          <button
            type="button"
            className={modoManual ? "active" : ""}
            role="tab"
            aria-selected={modoManual}
            onClick={() => setModoManual(true)}
          >
            <SlidersHorizontal size={16} /> Escolher músicas
          </button>
        </div>

        {!modoManual ? (
          <>
            <div className="journey-presets">
              {perfis.map((perfil) => (
                <button
                  type="button"
                  key={perfil.id}
                  className={`journey-preset-card ${perfilSelecionado === perfil.id ? "selected" : ""}`}
                  onClick={() => setPerfilSelecionado(perfil.id)}
                  aria-pressed={perfilSelecionado === perfil.id}
                >
                  <strong>{perfil.nome}</strong>
                  <span>{perfil.descricao}</span>
                  <span className="journey-preset-bpm">
                    Início: {perfil.bpm_inicial.min.toFixed(2)}–{perfil.bpm_inicial.max.toFixed(2)}
                    <ArrowRight size={14} />
                    Fim: {perfil.bpm_final.min.toFixed(2)}–{perfil.bpm_final.max.toFixed(2)}
                  </span>
                </button>
              ))}
              {perfis.length === 0 && !mensagem && (
                <p className="journey-loading">Carregando caminhos disponíveis...</p>
              )}
            </div>

            {perfilAtual && (
              <p className="journey-selection-note">
                As faixas inicial e final respeitam esses intervalos. A rota minimiza o custo acumulado das transições entre todas as características de áudio.
              </p>
            )}

            <button
              className="journey-button"
              onClick={iniciarPercursoPredefinido}
              disabled={carregando || !perfilSelecionado}
            >
              <Search size={18} />
              {carregando ? "Calculando caminho..." : "Gerar este percurso"}
            </button>
          </>
        ) : (
          <>
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
          </>
        )}

        {mensagem && <p className="journey-message" role="status">{mensagem}</p>}
      </div>

      {percurso.length > 0 && (
        <div className="journey-result">
          <h2>
            {perfilGerado ? `${perfilGerado.nome} — ` : ""}Seu percurso musical ({percurso.length} faixas)
          </h2>
          {perfilGerado && (
            <p className="journey-result-route">
              BPM normalizado: {perfilGerado.bpm_inicial.min.toFixed(2)}–{perfilGerado.bpm_inicial.max.toFixed(2)}
              {" → "}
              {perfilGerado.bpm_final.min.toFixed(2)}–{perfilGerado.bpm_final.max.toFixed(2)}
            </p>
          )}
          <div className="journey-playlist">
            {percurso.map((item) => (
              <div key={item.track_id} className="journey-embed-card">
                <div className="journey-track-metadata">
                  <span><Activity size={15} /> BPM normalizado</span>
                  <strong>
                    {typeof item.bpm === "number" && Number.isFinite(item.bpm)
                      ? item.bpm.toFixed(3)
                      : "N/D"}
                  </strong>
                </div>
                <div className="journey-embed-frame">
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
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="journey-info">
        <div className="journey-info-icon"><Music2 size={22} /></div>
        <div>
          <h2>Transições pensadas faixa a faixa</h2>
          <p>O A* compara o custo de cada aresta, combinando BPM, energia, estilo, harmonia e popularidade. Os caminhos prontos definem apenas os intervalos de BPM das faixas inicial e final; você também pode escolher as duas músicas manualmente.</p>
        </div>
      </div>
    </section>
  );
}