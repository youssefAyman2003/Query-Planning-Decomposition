# Query Planning Decomposition

Advanced RAG app that plans a complex question, splits it into focused sub-queries, retrieves evidence for each one, then writes a single answer. Chat and embeddings run through **Ollama** (`langchain-ollama`). The backend is FastAPI; the UI is a red, black, and white workspace.

## Architecture

```
main.py                 FastAPI app (UI + JSON API)
configs/config.py       Settings from environment
src/pipeline.py         LangGraph pipeline (ChatOllama + OllamaEmbeddings)
src/nodes.py            Planner, retriever, responder
src/ingestion.py        Web load → split → FAISS
templates/              UI markup
static/                 CSS and JS
```

Flow: `planner → retriever → responder`.

## Prerequisites

Install [Ollama](https://ollama.com) and pull the models used by this app:

```bash
ollama pull llama3.2:3b
ollama pull bge-m3:latest
```

Ollama should be running at `http://localhost:11434` (or set `OLLAMA_BASE_URL`).

## Setup

```bash
cp .env.example .env
pip install -r requirements.txt
python main.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

The first start builds the vector index from the configured source URLs using `bge-m3`. The status pill in the header shows when the index is ready.

## API

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/` | App UI |
| `GET` | `/api/status` | Index ready / init error |
| `POST` | `/api/query` | `{ "question": "..." }` → plan, sources, answer |

Example:

```bash
curl -X POST http://127.0.0.1:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question":"Explain how agent loops work and what are the challenges in diffusion video generation?"}'
```

## Docker

The container talks to Ollama on the host via `host.docker.internal`. Keep Ollama running locally, then:

```bash
docker build -t query-planning-decomposition .
docker run --rm -p 8000:8000 --env-file .env --add-host=host.docker.internal:host-gateway query-planning-decomposition
```

If `.env` still points at `localhost`, override it:

```bash
docker run --rm -p 8000:8000 \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  query-planning-decomposition
```

Then open [http://localhost:8000](http://localhost:8000).
