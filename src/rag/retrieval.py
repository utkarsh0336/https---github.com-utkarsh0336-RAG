import os
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer, CrossEncoder
from langchain_core.documents import Document
from src.cache import RedisCache

class HybridRetriever:
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        
        try:
            self.client = QdrantClient(url=qdrant_url)
        except Exception as e:
            print(f"Failed to connect to Qdrant: {e}")
            self.client = None
            
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        # Re-enable CrossEncoder for better re-ranking
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        
        # Initialize cache
        try:
            self.cache = RedisCache()
        except Exception as e:
            print(f"Redis cache not available: {e}")
            self.cache = None

    def search(self, query: str, k: int = 10) -> List[Document]:
        """Performs hybrid search with dense retrieval + CrossEncoder re-ranking + vector caching."""
        if not self.client:
            print("Qdrant client not initialized.")
            return []
        
        # Try to get cached vector first (Tier 2)
        query_vector = None
        if self.cache:
            query_vector = self.cache.get_vector(query)
            if query_vector:
                print(f"✓ Cache hit: vector for '{query[:30]}...'")
        
        # If not cached, encode and cache it
        if query_vector is None:
            query_vector = self.model.encode(query).tolist()
            if self.cache:
                self.cache.set_vector(query, query_vector)
        
        try:
            # 1. Retrieve top 2*k candidates using dense vector search
            from qdrant_client.models import PointStruct, VectorParams, Distance
            
            results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=k * 2  # Retrieve more candidates for re-ranking
            ).points
        except Exception as e:
            print(f"Search failed: {e}")
            return []
        
        if not results:
            return []
            
        # 2. Re-rank results using CrossEncoder
        documents = []
        passages = []
        for res in results:
            text = res.payload.get("text", "")
            passages.append([query, text])
            documents.append(Document(
                page_content=text,
                metadata=res.payload
            ))
            
        # Score all query-document pairs
        scores = self.reranker.predict(passages)
        
        # Sort by re-ranking score (higher is better)
        ranked_results = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
        
        # Return top k after re-ranking
        return [doc for doc, score in ranked_results[:k]]

class MultiSourceRetriever:
    def __init__(self):
        self.wiki_retriever = HybridRetriever("wiki_rag")
        self.arxiv_retriever = HybridRetriever("arxiv_rag")
        
    def retrieve(self, query: str, source: str = "all") -> List[Document]:
        docs = []
        if source in ["all", "wiki"]:
            try:
                docs.extend(self.wiki_retriever.search(query))
            except Exception as e:
                print(f"Wiki retrieval failed: {e}")
                
        if source in ["all", "arxiv"]:
            try:
                docs.extend(self.arxiv_retriever.search(query))
            except Exception as e:
                print(f"ArXiv retrieval failed: {e}")
                
        return docs
