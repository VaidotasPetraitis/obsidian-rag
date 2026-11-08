"""Run: python -m uvicorn app:app --host 127.0.0.1 --port 8000"""
import logging
from typing import Literal

import httpx
import psycopg
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.exc import SQLAlchemyError

import rag
from rag import config

app = FastAPI(title='Obsidian LangChain RAG learning lab', version='2.0.0',
              description='Windows Ollama + PostgreSQL/pgvector. Start with POST /ingest, then /retrieve or /ask.')


class Question(BaseModel):
    question: str = Field(min_length=1, max_length=config.MAX_QUESTION_LENGTH)
    level: Literal['similarity', 'mmr'] = 'similarity'
    k: int = Field(default=config.DEFAULT_K, ge=1, le=config.MAX_K)

    @field_validator('question')
    @classmethod
    def _nonblank(cls, value):
        if not value.strip():
            raise ValueError('Question cannot be blank.')
        return value.strip()


@app.exception_handler(ValueError)
async def configuration_error(request, error):
    return JSONResponse(status_code=409, content={'detail': str(error)})


@app.exception_handler(psycopg.Error)
@app.exception_handler(SQLAlchemyError)
@app.exception_handler(httpx.HTTPError)
@app.exception_handler(ConnectionError)
async def dependency_error(request, error):
    logging.error('Local RAG dependency failed', exc_info=error)
    return JSONResponse(
        status_code=503,
        content={'detail': 'PostgreSQL or Ollama unavailable. Check service/model status and server logs.'},
    )


@app.get('/health')
def health():
    service = rag.get_service()
    chunk_count = service.document_index.count()
    models = rag.list_models()
    required_models = {config.CHAT_MODEL, config.EMBED_MODEL}
    if not required_models.issubset(models):
        raise HTTPException(503, 'Required Ollama models missing.')

    return {'status': 'ok', 'chunks': chunk_count, 'models': models}


@app.post('/ingest')
def ingest():
    return rag.ingest()


@app.post('/retrieve')
def retrieve(body: Question):
    return rag.retrieve(
        question=body.question,
        level=body.level,
        k=body.k,
    )


@app.post('/ask')
def ask(body: Question):
    return rag.ask(
        question=body.question,
        level=body.level,
        k=body.k,
    )
