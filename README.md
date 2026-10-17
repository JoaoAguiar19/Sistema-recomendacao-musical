# Sistema de Recomendação Musical por Grafos

## Visão Geral
O projeto consiste no desenvolvimento de uma aplicação de recomendação e organização musical baseada em busca em grafos.
Cada vértice representa uma música, e as conexões representam relações entre faixas, considerando características como 
gênero musical, artista, ritmo, BPM e tonalidade.

O objetivo é utilizar algoritmos de busca heurística para gerar sequências de músicas que atendam às preferênciasdo usuário, 
buscando transições musicais coerentes de acordo com os critérios definidos.

## Funcionalidades Propostas
* **Descoberta Musical:** Permitir que o usuário escolha uma música inicial e receba recomendações de faixas para continuar a reprodução, mantendo a coerência.
* **Transição entre duas músicas (Ponto Central):** Permitir que o usuário selecione uma música inicial (A) e uma música de destino (B). O sistema buscará o caminho mais eficiente de faixas intermediárias que conecte as duas, minimizando diferenças bruscas.
  * *Pesos Dinâmicos (Diferencial):* Ajuste da prioridade da transição (foco no ritmo, no gênero ou equilibrado).
* **Geração de playlists personalizadas:** Geração a partir de critérios próprios ou temas (ex: felicidade, tristeza), filtrando os nós do grafo.

## Ferramentas e Tecnologias
* **Backend:** Python, FastAPI, NetworkX (Grafos), Pandas (Dados).
* **Integração:** Spotify Web API (extração de áudio features).
* **Banco de Dados:** PostgreSQL e SQLAlchemy (ORMs), orquestrados via Docker.
* **Frontend:** React + Vite ou HTML/CSS/JS (Vanilla).

---

## Como rodar o projeto localmente

### 1. Pré-requisitos
Certifique-se de ter instalado em sua máquina:
* [Python 3.10+](https://www.python.org/downloads/)
* [Docker e Docker Compose](https://docs.docker.com/get-docker/)
* [Git](https://git-scm.com/)

### 2. Clonar o repositório
Abra o terminal e clone o projeto. Em seguida, mude para a branch de desenvolvimento:
```bash
git clone https://github.com/JoaoAguiar19/Sistema-recomendacao-musical.git
cd sistema-recomendacao-musical
git checkout develop
```

### 3. Subir o Banco de Dados (Docker)
Na raiz do projeto, execute o comando abaixo para iniciar o contêiner do PostgreSQL:
```bash
docker-compose up -d
```
### 4. Configurar o Ambiente Python
Acesse a pasta do backend, crie e ative o ambiente virtual:

Linux/macOS:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

Windows:
```bash
cd backend
python -m venv venv
venv\Scripts\activate
```

### 5. Instalar as Dependências
Com o ambiente virtual ativado, instale os pacotes necessários:
```bash
pip install -r requirements.txt
```

### 6. Iniciar a API
Ainda dentro de backend, suba o servidor da aplicação:
```bash
uvicorn app.main:app --reload
```

---

## Links úteis após a inicialização:

 * Documentação (Swagger): http://127.0.0.1:8000/docs

 * Teste de Conexão com DB: http://127.0.0.1:8000/teste-db

### 7. Encerrar a Aplicação

 * Pressione Ctrl + C no terminal da API.

 * Desative o ambiente virtual rodando: deactivate

 * Na raiz do projeto, desligue o banco de dados: docker-compose down

### Observações

 * O Docker precisa estar em execução antes de iniciar a API.

 * Certifique-se de que o ambiente virtual está ativado antes de rodar qualquer comando do Python/pip.

 * Verifique se as variáveis de conexão com o banco no backend correspondem ao docker-compose.yml (normalmente em localhost ou 127.0.0.1).
