from redis import StrictRedis

redis_client = StrictRedis(
    host="localhost",
    port=6379,
    db=0,
)
