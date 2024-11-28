import os
import redis

r = redis.Redis(host=os.getenv('REDIS_HOST', 'redis'), port=os.getenv('REDIS_PORT', 6379), decode_responses=True)
