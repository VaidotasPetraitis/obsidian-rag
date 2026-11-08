# MMR RAG

Maximal marginal relevance (MMR) balances relevance to the question with diversity among selected passages. It can reduce repeated evidence from overlapping chunks.

Indexing and answer generation are identical to [similarity RAG](01-similarity.md). Only passage selection changes.

## Retrieval

```text
Question -> query embedding -> candidate chunks -> diverse selection -> optional Llama answer
```

[Retrieval](../rag/retrieval.py) embeds the question and calls `max_marginal_relevance_search_with_score_by_vector()`.

Settings in [config.py](../rag/config.py) control selection:

- `k`: maximum number of returned chunks; defaults to 4.
- `MMR_FETCH_K=20`: baseline candidate pool size.
- `MMR_FETCH_MULTIPLIER=3`: the pool grows to `max(20, k * 3)`.
- `MMR_LAMBDA_MULT=0.5`: balances relevance and diversity. Nearer 1 favors relevance; nearer 0 favors diversity.

## Request

Use this body with `/retrieve` or `/ask`:

```json
{
  "question": "What do these notes say about distributed-system consistency?",
  "level": "mmr",
  "k": 4
}
```

Returned `cosine_distance` values describe relevance to the original question, not MMR's diversity objective. The application preserves the store's returned order.

MMR can provide broader evidence, but diversity may displace a more relevant passage. It adds no query expansion or extra chat-model call.

[Project README](../README.md)
