from typing import List
from sqlmodel import SQLModel


class ItemSummary(SQLModel):
    name: str
    quantity: int
    price: float
    total: float


class OrderSummary(SQLModel):
    customer_id: int
    customer_name: str
    items_ordered: List[ItemSummary]


class PaginatedOrderSummary(SQLModel):
    date: str
    page: int
    per_page: int
    total_pages: int
    total_orders: int
    orders: List[OrderSummary]
