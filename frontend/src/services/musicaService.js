import api from './api';

export const obterMusicas = async (busca = '', limite = 50) => {
  const response = await api.get('/musicas', {
    params: {
      busca: busca || undefined,
      limite: limite
    }
  });
  return response.data;
};