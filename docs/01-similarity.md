# Similarity RAG

Retrieves the passages closest to a question, then optionally generates an answer from them. This is the default strategy.

## Indexing

`POST /ingest` runs the shared indexing pipeline:

1. Read Markdown notes from the configured vault.
2. Split them into chunks using `CHUNK_SIZE` and `CHUNK_OVERLAP` from [config.py](../rag/config.py).
3. Generate document embeddings with `nomic-embed-text`.
4. Store the text, metadata, and vectors in PostgreSQL/pgvector.

LangChain skips unchanged chunks and removes stale ones. Run ingestion again after adding, editing, or deleting notes. Both strategies use this same index.

## Retrieval and answering

```text
Question -> query embedding -> closest chunks -> optional Llama answer
```

[Retrieval](../rag/retrieval.py) calls `similarity_search_with_score()` to return up to `k` chunks from the full index.

- `/retrieve` returns passages and their cosine distances. Lower distance means a closer match.
- `/ask` also sends those passages to `llama3.1:8b` through a LangChain document chain. The answer includes numbered citations matching the returned sources.

No passages means a fixed refusal without calling Llama. There is no relevance threshold, so unrelated questions can still return passages; distances are not confidence scores.

## Request

Use this body with `/retrieve` or `/ask`:

```json
{
  "question": "What is a content delivery network?",
  "level": "similarity",
  "k": 4
}
```

Similarity can return repetitive, overlapping chunks. [MMR](02-mmr.md) adds diversity to passage selection.

[Project README](../README.md)
