from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import menu, employees, customers, orders
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("FastAPI app is starting...")
    yield
    # Shutdown
    logger.info("FastAPI app is shutting down...")

app = FastAPI(lifespan=lifespan)

app.include_router(menu.router)
app.include_router(employees.router)
app.include_router(customers.router)
app.include_router(orders.router)
