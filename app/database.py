from sqlmodel import SQLModel, create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)
# Creates the database connection engine

# Needed by FastAPI routes to access the DB session


def get_session():
    # FastAPI dependency that gives a new DB session per request
    with Session(engine) as session:
        # opens a database connection, hands it over to your route
        # automatically closes it after the request is done
        yield session
