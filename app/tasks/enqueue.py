import asyncio
# for running asynchronous code
import os
from arq.connections import create_pool, RedisSettings
# create_pool connects to Redis
# RedisSettings allows ARQ to configure Redis from a URL


# these funcs triggers the bg task from the API
async def enqueue(order_id: int):
    # async function
    redis = await create_pool(
        RedisSettings.from_dsn(os.getenv("REDIS_URL", "redis://redis:6379")))
    await redis.enqueue_job("update_order_status", order_id)
    # enqueues the job called the func name with parameter


# since the router is sync func, it is not await compatible. So this:
def enqueue_sync(order_id: int):
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(enqueue(order_id))
        # tries to get current running event loop
        # if it finds, enqueue func is scheduled in bg without blocking
    except RuntimeError:
        asyncio.run(enqueue(order_id))
        # if no running loop, just runs enqueue
