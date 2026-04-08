import chromadb
from chromadb.config import Settings


class ChromaStore:

    def __init__(self, path):
        self.client = chromadb.Client(
            Settings(persist_directory=path)
        )

        self.collection = self.client.get_or_create_collection(
            name="resume_collection"
        )

    def add(self, doc_id, embedding, metadata, document):

        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            metadatas=[metadata],
            documents=[document]
        )

    def search(self, embedding, n_results=5, where=None):

        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=n_results,
            where=where
        )

        return results