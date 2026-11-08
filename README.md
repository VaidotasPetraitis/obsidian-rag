# Obsidian RAG

A local RAG API that searches an Obsidian vault and generates answers with source citations.

Built with Python, FastAPI, LangChain, Windows Ollama, and PostgreSQL/pgvector in Docker.

## Features

- Index Markdown notes without modifying the vault.
- Skip unchanged chunks and remove stale chunks when re-indexing.
- Search with similarity or MMR for more diverse passages.
- Retrieve passages with cosine distances or generate answers with source citations.
- Configure chunk size, overlap, retrieval settings, and model limits.
- Run models locally with Ollama and persist indexed data in PostgreSQL.

## Models

- `llama3.1:8b` — answer generation.
- `nomic-embed-text:latest` — 768-dimensional embeddings.

## Getting started

With Docker Desktop and Ollama running, dependencies installed, and `.env` configured for your vault, start the application:

```powershell
.\start.bat
```

Open [Swagger UI](http://127.0.0.1:8000/docs) to use the API:

1. Run `POST /ingest` to index your notes. Run it again after changing the vault.
2. Use `POST /retrieve` to search passages or `POST /ask` to generate an answer.
3. Choose `similarity` or `mmr` in the request's `level` field.

`GET /health` checks database access, stored chunk count, and installed model names.

## Configuration

Connection URLs, model names, vault path, and excluded directories are configured in `.env`.

Chunk size, overlap, retrieval settings, model limits, and timeouts are defined in [rag/config.py](rag/config.py). Restart the API after editing settings. Changing chunking or embedding settings requires rebuilding the index or using a separate compatible database.

## Documentation

- [Similarity RAG](docs/01-similarity.md): ingestion, embeddings, storage, retrieval, and answer generation.
- [MMR RAG](docs/02-mmr.md): diverse passage selection, configuration, and tradeoffs.

## Project structure

- `app.py` — FastAPI endpoints.
- `rag/` — indexing, retrieval, and answer generation.
- `compose.yaml` — PostgreSQL/pgvector service.
- `start.bat` — database and API startup.

The vault is read without modification. Indexed data persists in the Docker volume. The API is intended for local use and has no authentication.
