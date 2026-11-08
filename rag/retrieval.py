"""Search strategies returning (document, cosine_distance) pairs."""
from . import config


class Retrieval:
    """Return the native search results; keep scores separate from documents."""

    def __init__(self, document_index, embeddings):
        self._document_index = document_index
        self._embeddings = embeddings
        self.strategies = {'similarity': self._similarity, 'mmr': self._mmr}

    def search(self, question, level, k):
        search = self.strategies.get(level)
        if search is None:
            raise ValueError('Unknown retrieval strategy.')
        self._document_index.store
        self._document_index.validate()
        return search(question, k)

    def _similarity(self, question, k):
        return self._document_index.store.similarity_search_with_score(question, k=k)

    def _mmr(self, question, k):
        query_vector = self._embeddings.embed_query(question)
        return self._document_index.store.max_marginal_relevance_search_with_score_by_vector(
            query_vector, k=k,
            fetch_k=max(config.MMR_FETCH_K, k * config.MMR_FETCH_MULTIPLIER),
            lambda_mult=config.MMR_LAMBDA_MULT,
        )
