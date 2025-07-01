import os
from arq.connections import RedisSettings

from app.tasks.order_tasks import update_order_status
from app.utils.logger import logger


async def startup(_):
    logger.info("ARQ worker starting...")


async def shutdown(_):
    logger.info("ARQ worker stopping...")


# registers the task with ARQ and tells it how to behave
class WorkerSettings:
    functions = [update_order_status]
    # tasks ARQ the tasks the worker can run
    on_startup = startup
    on_shutdown = shutdown
    # looks for these func for logging
    redis_settings = RedisSettings.from_dsn(
        os.getenv("REDIS_URL", "redis://redis:6379"))
    job_timeout = 1200   # (20 minutes)
    # max time a task can run. After this time, it will get cancelled
