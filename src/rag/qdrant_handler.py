import os
from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Any

class QdrantHandler:
    def __init__(self, url: str = None, api_key: str = None):
        self.url = url or os.getenv("QDRANT_URL", "http://localhost:6333")
        self.client = QdrantClient(url=self.url, api_key=api_key)

    def create_collection(self, collection_name: str, vector_size: int = 384):
        """Creates a collection if it doesn't exist."""
        if not self.client.collection_exists(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance.COSINE
                )
            )
            print(f"Collection '{collection_name}' created.")
        else:
            print(f"Collection '{collection_name}' already exists.")

    def add_documents(self, collection_name: str, documents: List[str], metadatas: List[Dict[str, Any]], embeddings: List[List[float]]):
        """Adds documents to the collection."""
        points = [
            models.PointStruct(
                id=idx,
                vector=embedding,
                payload={"text": doc, **meta}
            )
            for idx, (doc, meta, embedding) in enumerate(zip(documents, metadatas, embeddings))
        ]
        
        # Batch upload (simplified for now, ideally chunked)
        self.client.upsert(
            collection_name=collection_name,
            points=points
        )
        print(f"Added {len(points)} documents to '{collection_name}'.")

    def search(self, collection_name: str, query_vector: List[float], limit: int = 5):
        """Searches for similar vectors."""
        return self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit
        )
