"""Environment settings shared by the RAG components."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
os.environ['LANGSMITH_TRACING'] = 'false'
os.environ['LANGCHAIN_TRACING_V2'] = 'false'
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://rag:local-rag-only@127.0.0.1:5433/rag')
OLLAMA_URL = os.getenv('OLLAMA_BASE_URL', 'http://127.0.0.1:11434')
CHAT_MODEL = os.getenv('CHAT_MODEL', 'llama3.1:8b')
EMBED_MODEL = os.getenv('EMBED_MODEL', 'nomic-embed-text:latest')
VAULT = Path(os.getenv('VAULT_PATH', 'C:/Users/Jetpack/Documents/dev/habits/Habits'))
EXCLUDED = set(os.getenv('EXCLUDE_DIRS', '.obsidian,.git,.trash,5 - Templates').split(','))
TABLE = 'lc_documents'

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
EMBEDDING_DIMENSIONS = 768
INDEX_BATCH_SIZE = 16

DEFAULT_K = 4
MAX_K = 8
MAX_QUESTION_LENGTH = 1000
MMR_FETCH_K = 20
MMR_FETCH_MULTIPLIER = 3
MMR_LAMBDA_MULT = 0.5

CHAT_TEMPERATURE = 0
CHAT_CONTEXT_TOKENS = 8192
CHAT_MAX_OUTPUT_TOKENS = 700

DB_CONNECT_TIMEOUT_SECONDS = 5
EMBEDDING_TIMEOUT_SECONDS = 180
CHAT_TIMEOUT_SECONDS = 300
HEALTH_TIMEOUT_SECONDS = 10

SIGNATURE = f'{VAULT.resolve()}|{EMBED_MODEL}|{EMBEDDING_DIMENSIONS}|{CHUNK_SIZE}|{CHUNK_OVERLAP}|nomic-prefix-v2'
REFUSAL = 'I could not find that in your notes.'
