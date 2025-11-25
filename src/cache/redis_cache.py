import redis
import json
import hashlib
import pickle
from typing import Optional, List, Any
from datetime import timedelta

class RedisCache:
    """Two-tier caching system for RAG pipeline."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.client = redis.from_url(redis_url, decode_responses=False)
        
        # TTL settings (in seconds)
        self.ANSWER_TTL = 3600  # 1 hour for final answers
        self.VECTOR_TTL = 86400  # 24 hours for embedded vectors
        self.WEB_DATA_TTL = 1800  # 30 minutes for web-sourced info (fresher)
        
    def _hash_key(self, text: str) -> str:
        """Generate consistent hash for cache keys."""
        return hashlib.sha256(text.encode()).hexdigest()[:16]
    
    # ----- TIER 1: Final Answer Caching -----
    
    def get_answer(self, query: str) -> Optional[str]:
        """Get cached final answer for exact query match."""
        key = f"answer:{self._hash_key(query)}"
        try:
            cached = self.client.get(key)
            if cached:
                return cached.decode('utf-8')
        except Exception as e:
            print(f"Cache get error: {e}")
        return None
    
    def set_answer(self, query: str, answer: str, ttl: Optional[int] = None):
        """Cache final answer for query."""
        key = f"answer:{self._hash_key(query)}"
        ttl = ttl or self.ANSWER_TTL
        try:
            self.client.setex(key, ttl, answer.encode('utf-8'))
        except Exception as e:
            print(f"Cache set error: {e}")
    
    def set_web_answer(self, query: str, answer: str):
        """Cache answer with web-sourced data (shorter TTL for freshness)."""
        self.set_answer(query, answer, ttl=self.WEB_DATA_TTL)
    
    # ----- TIER 2: Vector Embedding Caching -----
    
    def get_vector(self, text: str) -> Optional[List[float]]:
        """Get cached embedding vector for text."""
        key = f"vector:{self._hash_key(text)}"
        try:
            cached = self.client.get(key)
            if cached:
                return pickle.loads(cached)
        except Exception as e:
            print(f"Vector cache get error: {e}")
        return None
    
    def set_vector(self, text: str, vector: List[float]):
        """Cache embedding vector for reuse."""
        key = f"vector:{self._hash_key(text)}"
        try:
            self.client.setex(key, self.VECTOR_TTL, pickle.dumps(vector))
        except Exception as e:
            print(f"Vector cache set error: {e}")
    
    def get_batch_vectors(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Get multiple cached vectors at once."""
        keys = [f"vector:{self._hash_key(t)}" for t in texts]
        try:
            cached = self.client.mget(keys)
            return [pickle.loads(v) if v else None for v in cached]
        except Exception as e:
            print(f"Batch vector cache error: {e}")
            return [None] * len(texts)
    
    def set_batch_vectors(self, texts: List[str], vectors: List[List[float]]):
        """Cache multiple vectors at once."""
        try:
            pipe = self.client.pipeline()
            for text, vector in zip(texts, vectors):
                key = f"vector:{self._hash_key(text)}"
                pipe.setex(key, self.VECTOR_TTL, pickle.dumps(vector))
            pipe.execute()
        except Exception as e:
            print(f"Batch vector cache set error: {e}")
    
    # ----- Cache Management -----
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern (e.g., "answer:*")."""
        try:
            for key in self.client.scan_iter(match=pattern):
                self.client.delete(key)
        except Exception as e:
            print(f"Cache invalidation error: {e}")
    
    def clear_all(self):
        """Clear entire cache (use with caution)."""
        try:
            self.client.flushdb()
        except Exception as e:
            print(f"Cache clear error: {e}")
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        try:
            info = self.client.info('stats')
            return {
                'total_keys': self.client.dbsize(),
                'hits': info.get('keyspace_hits', 0),
                'misses': info.get('keyspace_misses', 0),
                'hit_rate': info.get('keyspace_hits', 0) / max(info.get('keyspace_hits', 0) + info.get('keyspace_misses', 1), 1)
            }
        except Exception as e:
            print(f"Stats error: {e}")
            return {}
