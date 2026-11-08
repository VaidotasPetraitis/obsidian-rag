"""Nomic embedding adapter used by LangChain."""
from langchain_ollama import OllamaEmbeddings

class NomicEmbeddings(OllamaEmbeddings):
    """Adapt Nomic's task prefixes to LangChain's existing embedding interface."""

    def embed_documents(self, texts):
        passages = ['search_document: ' + text for text in texts]
        return super().embed_documents(passages)

    def embed_query(self, text):
        vectors = super().embed_documents(['search_query: ' + text])
        return vectors[0]

    async def aembed_documents(self, texts):
        passages = ['search_document: ' + text for text in texts]
        return await super().aembed_documents(passages)

    async def aembed_query(self, text):
        vectors = await super().aembed_documents(['search_query: ' + text])
        return vectors[0]
