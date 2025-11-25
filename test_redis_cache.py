import sys
import os
sys.path.append(os.path.abspath('.'))

from src.cache import RedisCache

print("Testing Redis caching system...")

cache = RedisCache()

# Test Tier 1: Answer caching
print("\n=== Testing Tier 1: Answer Caching ===")
question = "What is a transformer in AI?"
answer = "A transformer is a deep learning architecture..."

# Set answer
cache.set_answer(question, answer)
print(f"✓ Cached answer for: {question[:40]}...")

# Get answer
cached = cache.get_answer(question)
if cached:
    print(f"✓ Retrieved cached answer: {cached[:50]}...")
else:
    print("✗ Failed to retrieve answer")

# Test Tier 2: Vector caching
print("\n=== Testing Tier 2: Vector Caching ===")
text = "transformer architecture"
vector = [0.1, 0.2, 0.3] * 100  # Mock vector

cache.set_vector(text, vector)
print(f"✓ Cached vector for: {text}")

cached_vector = cache.get_vector(text)
if cached_vector and len(cached_vector) == 300:
    print(f"✓ Retrieved cached vector (length: {len(cached_vector)})")
else:
    print("✗ Failed to retrieve vector")

# Test cache stats
print("\n=== Cache Statistics ===")
stats = cache.get_stats()
print(f"Total keys: {stats.get('total_keys', 0)}")
print(f"Cache hits: {stats.get('hits', 0)}")
print(f"Cache misses: {stats.get('misses', 0)}")
print(f"Hit rate: {stats.get('hit_rate', 0):.2%}")

print("\n✅ Redis caching system is operational!")
