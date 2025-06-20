from sqlmodel import SQLModel, Field
from typing import Optional
from pydantic import field_validator
from datetime import date


# DB Model
class Employee(SQLModel, table=True):
    __tablename__ = "employees"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    role: str = Field(max_length=50)
    email: str = Field(max_length=120, sa_column_kwargs={"unique": True})
    phone: Optional[str] = Field(
        default=None, max_length=20, sa_column_kwargs={"unique": True})
    hire_date: date

    def __repr__(self):
        return f"<Employee {self.name} (${self.role})>"


# Create Schema
class EmployeeCreate(SQLModel):
    name: str
    role: str
    email: str
    phone: Optional[str] = None
    hire_date: date

    @field_validator("name", "role", "email")
    def not_empty(cls, v):
        if not v.strip():
            raise ValueError("Field cannot be empty")
        return v


# Read Schema
class EmployeeRead(SQLModel):
    id: int
    name: str
    role: str
    email: str
    phone: Optional[str]
    hire_date: date


# Update Schema
class EmployeeUpdate(SQLModel):
    name: Optional[str] = None
    role: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    hire_date: Optional[date] = None

    @field_validator("name", "role", "email")
    def not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Field cannot be empty")
        return v
