import os

import redis

redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = int(os.getenv("REDIS_PORT", 6379))

redis_client = redis.Redis(host=redis_host, port=redis_port, db=0, decode_responses=True)
