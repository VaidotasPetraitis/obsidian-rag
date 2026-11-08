"""Read Obsidian notes and split them into numbered passages."""
from pathlib import Path
from langchain_community.document_loaders import TextLoader

class VaultNotes:
    """Read permitted Markdown files and split them into chunks. Never modify the vault."""

    def __init__(self, root, excluded, splitter):
        self._root = Path(root)
        self._excluded = set(excluded)
        self._splitter = splitter

    def load(self):
        self._require_directory()
        documents = []
        for path in self._paths():
            documents.extend(self._read(path))
        self._require_content(documents)
        return documents

    def split(self, documents):
        chunks = []
        for document in documents:
            chunks.extend(self._split_note(document))
        return chunks

    def _split_note(self, document):
        chunks = self._splitter.split_documents([document])
        for chunk_index, chunk in enumerate(chunks):
            chunk.metadata['chunk_index'] = chunk_index
        return chunks

    def _require_directory(self):
        if not self._root.is_dir():
            raise ValueError(f'Vault directory does not exist: {self._root}')

    def _paths(self):
        for path in sorted(self._root.rglob('*.md')):
            if self._allowed(path):
                yield path

    def _allowed(self, path):
        if path.is_symlink():
            return False
        if not self._excluded.isdisjoint(path.relative_to(self._root).parts):
            return False
        return path.resolve().is_relative_to(self._root.resolve())

    def _read(self, path):
        documents = TextLoader(str(path), encoding='utf-8-sig').load()
        for document in documents:
            document.metadata['source'] = path.relative_to(self._root).as_posix()
        return documents

    def _require_content(self, documents):
        if not any(document.page_content.strip() for document in documents):
            raise ValueError('No nonempty Markdown notes found; refusing to clear the index.')
