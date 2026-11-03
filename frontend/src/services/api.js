import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000', // Certifique-se de que é a porta onde seu FastAPI está rodando
});

export default api;

