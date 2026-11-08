"""Start here: the ingestion, retrieval, and answering workflows."""
from . import config
from .config import REFUSAL

class RagService:
    """Orchestrate use cases. Collaborators are injected and can be replaced independently."""

    def __init__(self, notes, document_index, retrieval, answerer):
        self._notes = notes
        self.document_index = document_index
        self._retrieval = retrieval
        self._answerer = answerer

    def ingest(self):
        documents = self._notes.load()
        chunks = self._notes.split(documents)
        result = self.document_index.write(chunks)
        summary = {'notes': len(documents), 'chunks': len(chunks)}
        summary.update(result)
        return summary

    def retrieve(self, question, level='similarity', k=config.DEFAULT_K):
        matches = self._retrieval.search(question, level, k)
        return {'strategy': level, 'sources': self._format_sources(matches)}

    def ask(self, question, level='similarity', k=config.DEFAULT_K):
        matches = self._retrieval.search(question, level, k)
        answer = REFUSAL
        if matches:
            documents = [document for document, _ in matches]
            answer = self._answerer.answer(question, documents)
        return {'answer': answer, 'strategy': level, 'sources': self._format_sources(matches)}

    @staticmethod
    def _format_sources(matches):
        sources = []
        for document, distance in matches:
            sources.append({'source': document.metadata['source'],
                            'chunk_index': document.metadata['chunk_index'],
                            'content': document.page_content,
                            'cosine_distance': float(distance)})
        return sources
