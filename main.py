from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import menu, employees, customers, orders, summary
from app.utils.logger import logger
from sqlmodel import SQLModel
from app.database import engine


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
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
app.include_router(summary.router)
