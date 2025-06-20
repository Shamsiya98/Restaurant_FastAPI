from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from pydantic import field_validator
from datetime import date
from sqlalchemy.sql import func

if TYPE_CHECKING:
    from .orders import Order

# DB Model


class Customer(SQLModel, table=True):
    __tablename__ = "customers"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    email: Optional[str] = Field(
        max_length=120, sa_column_kwargs={"unique": True})
    phone: Optional[str] = Field(default=None, max_length=20)
    joined_date: Optional[date] = Field(default=None, sa_column_kwargs={
                                        "server_default": func.now()})

    orders: List["Order"] = Relationship(back_populates="customer")

    def __repr__(self):
        return f"<Customer {self.name}>"


# Create Schema
class CustomerCreate(SQLModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None

    @field_validator("name")
    def not_empty(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v


# Read Schema
class CustomerRead(SQLModel):
    id: int
    name: str
    email: Optional[str]
    phone: Optional[str]
    joined_date: Optional[date]


# Update Schema
class CustomerUpdate(SQLModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

    @field_validator("name")
    def not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Name cannot be empty")
        return v
