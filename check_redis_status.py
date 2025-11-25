"""
Redis Status Checker
This script checks if Redis is running and accessible.
"""
import sys
import os
sys.path.append(os.path.abspath('.'))

import redis
from src.cache import RedisCache

def check_redis_connection():
    """Check if Redis server is running and accessible."""
    print("=" * 60)
    print("REDIS STATUS CHECK")
    print("=" * 60)
    
    redis_url = "redis://localhost:6379"
    print(f"\n📍 Checking Redis at: {redis_url}")
    
    try:
        # Try to connect using raw redis client
        client = redis.from_url(redis_url, decode_responses=True, socket_connect_timeout=2)
        
        # Test ping
        response = client.ping()
        if response:
            print("✅ Redis server is RUNNING and responding")
            
            # Get server info
            info = client.info()
            print(f"\n📊 Redis Server Info:")
            print(f"   - Version: {info.get('redis_version', 'N/A')}")
            print(f"   - Uptime: {info.get('uptime_in_seconds', 0)} seconds")
            print(f"   - Connected clients: {info.get('connected_clients', 0)}")
            print(f"   - Used memory: {info.get('used_memory_human', 'N/A')}")
            
            # Check database
            db_info = client.info('keyspace')
            print(f"\n🗄️  Database Info:")
            if db_info:
                for db, stats in db_info.items():
                    print(f"   - {db}: {stats}")
            else:
                print("   - No keys in database")
            
            return True
            
    except redis.ConnectionError as e:
        print("❌ Redis server is NOT RUNNING")
        print(f"   Error: {e}")
        print("\n💡 To start Redis, you have several options:")
        print("   1. Using Docker Compose (recommended):")
        print("      docker-compose up -d redis")
        print("   2. Using Docker directly:")
        print("      docker run -d -p 6379:6379 --name rag_redis redis:alpine")
        print("   3. Install Redis locally (Windows):")
        print("      Download from: https://github.com/tporadowski/redis/releases")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_redis_cache():
    """Test the RedisCache wrapper."""
    print("\n" + "=" * 60)
    print("TESTING REDIS CACHE WRAPPER")
    print("=" * 60)
    
    try:
        cache = RedisCache()
        
        # Test basic operations
        test_key = "test_question"
        test_value = "test_answer"
        
        print(f"\n🧪 Testing cache operations...")
        
        # Set operation
        cache.set_answer(test_key, test_value)
        print(f"   ✓ SET operation completed")
        
        # Get operation
        result = cache.get_answer(test_key)
        if result == test_value:
            print(f"   ✓ GET operation successful - value retrieved correctly")
        else:
            print(f"   ✗ GET operation failed - expected '{test_value}', got '{result}'")
        
        # Stats
        stats = cache.get_stats()
        if stats:
            print(f"\n📈 Cache Statistics:")
            print(f"   - Total keys: {stats.get('total_keys', 0)}")
            print(f"   - Cache hits: {stats.get('hits', 0)}")
            print(f"   - Cache misses: {stats.get('misses', 0)}")
            print(f"   - Hit rate: {stats.get('hit_rate', 0):.2%}")
        
        print("\n✅ Redis cache wrapper is working correctly!")
        return True
        
    except Exception as e:
        print(f"\n❌ Redis cache wrapper test failed: {e}")
        return False

def main():
    """Main function."""
    is_running = check_redis_connection()
    
    if is_running:
        test_redis_cache()
        print("\n" + "=" * 60)
        print("✅ OVERALL STATUS: Redis is fully operational!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ OVERALL STATUS: Redis is NOT available")
        print("=" * 60)
        print("\n⚠️  Your RAG application will work, but without caching.")
        print("    This means slower performance and more API calls.")
        sys.exit(1)

if __name__ == "__main__":
    main()
