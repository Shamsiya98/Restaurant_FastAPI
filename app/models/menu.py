from sqlmodel import SQLModel, Field, Relationship
# SQLModel: lets us define both database models and Pydantic-style request/response models in one
# Field: Used to give extra information about each column/field
from typing import Optional, List, TYPE_CHECKING
# Optional[...]: Tells Python that a field can be None
from pydantic import field_validator
# to define custom validators

if TYPE_CHECKING:
    from .order_items import OrderItem


# DB Model
class MenuItem(SQLModel, table=True):
    # table=True: To let SQLModel know it should create and map to a db table
    # the table will be created from scratch if we call create _all()
    __tablename__ = "menu_items"
    # Optional in SQLModel, it will infer the tablename default as menuitem

    id: Optional[int] = Field(default=None, primary_key=True)
    # creates column id, Optional because auto-generated
    # Field(...): Tells SQLModel it is pk and should default to None
    # (so the DB will auto-generate it)
    name: str = Field(max_length=100, sa_column_kwargs={"unique": True})
    # required column, sqlalchemy setting: unique
    description: Optional[str] = None
    price: float
    category: str = Field(max_length=50)
    preparation_time_minutes: int

    order_items: List["OrderItem"] = Relationship(back_populates="menu_item")

    def __repr__(self):
        return f"<MenuItem {self.name} (${self.price})>"

# POST route will expect an id in the input - which the client shouldn't provide
# "422 Unprocessable Entity" if the client doesn't send id
# "IntegrityError" if they send an id that's already used
# So, we use separate schemas


# Create Schema (used in POST)
class MenuItemCreate(SQLModel):
    name: str
    description: Optional[str] = None
    price: float
    category: str
    preparation_time_minutes: int

    @field_validator("name", "category")
    def not_empty(cls, v):
        if not v.strip():
            raise ValueError("Field cannot be empty")
        return v

    @field_validator("price", "preparation_time_minutes")
    def must_be_positive(cls, v):
        # cls: a reference to the class the validator belongs to
        # value: the value of the field being validated
        if v is not None and v <= 0:
            raise ValueError("Value must be greater than 0")
        return v


# Read Schema (used in GET response)
class MenuItemRead(SQLModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    category: str
    preparation_time_minutes: int


# Update Schema (used in PATCH response)
class MenuItemUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    preparation_time_minutes: Optional[int] = None

    @field_validator("name", "category")
    def not_empty(cls, v):
        if not v.strip():
            raise ValueError("Field cannot be empty")
        return v

    @field_validator("price", "preparation_time_minutes")
    def must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Value must be greater than 0")
        return v
