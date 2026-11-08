"""Assemble the RAG components and expose the API used by app.py."""
from functools import lru_cache
import httpx
from langchain_ollama import ChatOllama
from langchain_text_splitters import RecursiveCharacterTextSplitter
from . import config
from .embeddings import NomicEmbeddings
from .notes import VaultNotes
from .storage import PostgresIndex
from .retrieval import Retrieval
from .answers import AnswerGenerator
from .service import RagService

@lru_cache(maxsize=1)
def get_service():
    """The only place where real dependencies are assembled."""
    embeddings = NomicEmbeddings(model=config.EMBED_MODEL,
                                 base_url=config.OLLAMA_URL,
                                 client_kwargs={'timeout': config.EMBEDDING_TIMEOUT_SECONDS})

    model = ChatOllama(model=config.CHAT_MODEL, base_url=config.OLLAMA_URL,
                       temperature=config.CHAT_TEMPERATURE,
                       num_ctx=config.CHAT_CONTEXT_TOKENS,
                       num_predict=config.CHAT_MAX_OUTPUT_TOKENS,
                       client_kwargs={'timeout': config.CHAT_TIMEOUT_SECONDS})

    document_index = PostgresIndex(config.DATABASE_URL, embeddings, config.SIGNATURE)
    retrieval = Retrieval(document_index, embeddings)
    splitter = RecursiveCharacterTextSplitter(chunk_size=config.CHUNK_SIZE, chunk_overlap=config.CHUNK_OVERLAP)
    notes = VaultNotes(config.VAULT, config.EXCLUDED, splitter)
    return RagService(notes, document_index, retrieval, AnswerGenerator(model))


def ingest():
    return get_service().ingest()


def retrieve(question, level='similarity', k=config.DEFAULT_K):
    return get_service().retrieve(question, level, k)


def ask(question, level='similarity', k=config.DEFAULT_K):
    return get_service().ask(question, level, k)


def list_models():
    with httpx.Client(timeout=config.HEALTH_TIMEOUT_SECONDS) as client:
        response = client.get(config.OLLAMA_URL + '/api/tags')
        response.raise_for_status()
        data = response.json()
    return [model['name'] for model in data['models']]
