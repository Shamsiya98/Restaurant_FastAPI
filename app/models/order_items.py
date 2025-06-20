
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from pydantic import field_validator

if TYPE_CHECKING:
    from .menu import MenuItem
    from .orders import Order


# DB Model
class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id")
    menu_item_id: int = Field(foreign_key="menu_items.id")
    quantity: int

    # Relationships
    menu_item: Optional["MenuItem"] = Relationship(
        back_populates="order_items")
    order: Optional["Order"] = Relationship(back_populates="items")


# Create Schema
class OrderItemCreate(SQLModel):
    menu_item_id: int
    quantity: int

    @field_validator("quantity")
    def quantity_positive(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be positive")
        return v


# Read-only nested schema for MenuItem inside an OrderItem
class MenuItemNested(SQLModel):
    id: int
    name: str
    price: float


# Read schema for OrderItem (for GET response)
class OrderItemRead(SQLModel):
    id: int
    menu_item_id: int
    quantity: int
    menu_item: MenuItemNested
