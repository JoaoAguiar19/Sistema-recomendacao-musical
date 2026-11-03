import api from './api';

export const obterMusicas = async (busca = '', limite = 50, offset = 0) => {
  const response = await api.get('/musicas', {
    params: {
      busca: busca || undefined,
      limite,
      offset
    }
  });
  return response.data;
};

export const obterPrevia = async (nome, artista) => {
  const response = await api.get('/preview', {
    params: { nome, artista }
  });
  return response.data.preview_url;
};

export const obterRecomendacoes = async (trackId, limite = 8) => {
  const response = await api.get(`/recomendacoes/${encodeURIComponent(trackId)}`, {
    params: { limite }
  });
  return response.data.musicas;
};