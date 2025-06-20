from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from pydantic import field_validator
from datetime import datetime
from sqlalchemy.sql import func

if TYPE_CHECKING:
    from .customers import Customer
    from .order_items import OrderItem, OrderItemCreate, OrderItemRead


# DB Model
class Order(SQLModel, table=True):
    __tablename__ = "orders"

    id: Optional[int] = Field(default=None, primary_key=True)
    customer_id: int = Field(foreign_key="customers.id")
    created_at: Optional[datetime] = Field(
        sa_column_kwargs={"server_default": func.now()})
    status: str = Field(default="Pending", max_length=20)

    # Relationships
    customer: Optional["Customer"] = Relationship(back_populates="orders")
    items: List["OrderItem"] = Relationship(
        back_populates="order",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


# Create Schema
class OrderCreate(SQLModel):
    customer_id: int
    status: Optional[str] = "Pending"
    items: List["OrderItemCreate"]

    @field_validator("status")
    def not_empty(cls, v):
        if not v.strip():
            raise ValueError("Status cannot be empty")
        return v


# Read Schema
class OrderRead(SQLModel):
    id: int
    customer_id: int
    created_at: datetime
    status: str
    items: List["OrderItemRead"]

# Update Schema


class OrderUpdate(SQLModel):
    customer_id: Optional[int] = None
    status: Optional[str] = None

    @field_validator("status")
    def not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Status cannot be empty")
        return v
