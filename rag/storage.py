"""PostgreSQL connections, schema checks, and vector-index persistence."""
from functools import cached_property
import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from langchain_classic.indexes import SQLRecordManager, index
from langchain_postgres import PGEngine, PGVectorStore
from . import config
from .config import TABLE

class PostgresIndex:
    """Own database connections, index initialization, and persistent indexing."""

    def __init__(self, database_url, embeddings, signature, table_name=TABLE):
        self._database_url = database_url
        self._embeddings = embeddings
        self._signature = signature
        self._table_name = table_name

    def initialize(self):
        self._create_metadata_table()
        self._create_vector_table()
        self._records

    @cached_property
    def store(self):
        self.initialize()
        return PGVectorStore.create_sync(engine=self._engine, table_name=self._table_name,
                                          embedding_service=self._embeddings)

    def validate(self):
        with self._connect() as connection:
            self._check_signature(connection)

    def write(self, chunks):
        store = self.store
        with self._connect() as connection:
            connection.execute('SELECT pg_advisory_xact_lock(726431)')
            self._check_signature(connection)
            result = index(chunks, self._records, store, cleanup='full',
                           source_id_key='source', batch_size=config.INDEX_BATCH_SIZE)
            connection.execute('INSERT INTO lc_rag_config VALUES (true, %s) '
                               'ON CONFLICT (singleton) DO NOTHING', (self._signature,))
        return result

    def count(self):
        with self._connect() as connection:
            self._check_signature(connection)
            query = sql.SQL('SELECT COUNT(*) AS chunk_count FROM {}').format(sql.Identifier(self._table_name))
            row = connection.execute(query).fetchone()
        return row['chunk_count']

    def _connect(self):
        return psycopg.connect(self._database_url, row_factory=dict_row,
                               connect_timeout=config.DB_CONNECT_TIMEOUT_SECONDS)

    @cached_property
    def _engine(self):
        url = self._database_url.replace('postgresql://', 'postgresql+asyncpg://', 1)
        return PGEngine.from_connection_string(url=url, connect_args={'timeout': config.DB_CONNECT_TIMEOUT_SECONDS})

    @cached_property
    def _records(self):
        url = self._database_url.replace('postgresql://', 'postgresql+psycopg://', 1)
        records = SQLRecordManager(namespace=self._table_name, db_url=url,
                                   engine_kwargs={'connect_args': {'connect_timeout': config.DB_CONNECT_TIMEOUT_SECONDS}})
        records.create_schema()
        return records

    def _create_metadata_table(self):
        with self._connect() as connection:
            connection.execute('CREATE EXTENSION IF NOT EXISTS vector')
            connection.execute('''CREATE TABLE IF NOT EXISTS lc_rag_config (
                singleton boolean PRIMARY KEY DEFAULT true CHECK (singleton),
                signature text NOT NULL
            )''')

    def _create_vector_table(self):
        with self._connect() as connection:
            connection.execute('SELECT pg_advisory_xact_lock(726432)')
            row = connection.execute('SELECT to_regclass(%s) AS name', (self._table_name,)).fetchone()
            if row['name'] is None:
                self._engine.init_vectorstore_table(table_name=self._table_name, vector_size=config.EMBEDDING_DIMENSIONS)

    def _check_signature(self, connection):
        row = connection.execute('SELECT signature FROM lc_rag_config WHERE singleton').fetchone()
        if row is None:
            return
        if row['signature'] != self._signature:
            raise ValueError('Index configuration changed. Use a separate database or restore the original vault/model/chunk settings.')
