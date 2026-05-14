import json
import redis
from app.core.config import REDIS_HOST, REDIS_PORT

# Initialize Redis client
# Using decode_responses=True to automatically decode responses to strings
try:
    redis_client = redis.Redis(
        host=REDIS_HOST or "localhost",
        port=REDIS_PORT or 6379,
        decode_responses=True,
        socket_timeout=5,
    )
    # Test connection
    redis_client.ping()
    print("Connected to Redis successfully.")
except Exception as e:
    print(f"Failed to connect to Redis: {e}")
    redis_client = None

def get_cache(key: str):
    if not redis_client:
        return None
    try:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
    except Exception as e:
        print(f"Redis get error: {e}")
    return None

def set_cache(key: str, data: dict, expire_seconds: int = 3600):
    if not redis_client:
        return False
    try:
        redis_client.setex(key, expire_seconds, json.dumps(data))
        return True
    except Exception as e:
        print(f"Redis set error: {e}")
        return False

def invalidate_cache(key_pattern: str):
    if not redis_client:
        return False
    try:
        # Note: keys() is generally not recommended in production for large datasets, 
        # but suitable for this project. Alternatively, use scan_iter.
        keys = redis_client.keys(key_pattern)
        if keys:
            redis_client.delete(*keys)
        return True
    except Exception as e:
        print(f"Redis invalidate error: {e}")
        return False
