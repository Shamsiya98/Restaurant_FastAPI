from sqlmodel import Session, select
from fastapi import HTTPException
from app.models import MenuItem, Employee, Customer
from typing import Optional


def check_menuitem_unique_name(
    session: Session,
        name: str,
        item_id: Optional[int] = None
):
    query = select(MenuItem).where(MenuItem.name == name)
    if item_id is not None:
        query = query.where(MenuItem.id != item_id)

    existing = session.exec(query).first()
    if existing:
        raise HTTPException(
            status_code=400, detail="Menu item with this name already exists")


def check_employee_unique_fields(
        session: Session,
        email: Optional[str],
        phone: Optional[str],
        emp_id: Optional[int] = None
):
    filters = []
    if email:
        filters.append(Employee.email == email)
    if phone:
        filters.append(Employee.phone == phone)

    if not filters:
        return  # Nothing to check

    query = select(Employee).where(*filters)
    if emp_id is not None:
        query = query.where(Employee.id != emp_id)

    existing = session.exec(query).first()
    if existing:
        if existing.email == email:
            raise HTTPException(
                status_code=400,
                detail="Another employee with this email already exists")
        if existing.phone == phone:
            raise HTTPException(
                status_code=400,
                detail="Another employee with this phone already exists")


def check_customer_unique_email(
    session: Session,
        email: str,
        customer_id: Optional[int] = None
):
    query = select(Customer).where(Customer.email == email)
    if customer_id is not None:
        query = query.where(Customer.id != customer_id)

    existing = session.exec(query).first()
    if existing:
        raise HTTPException(
            status_code=400, detail="Customer with this email already exists")


def validate_customer_exists(session: Session, customer_id: int):
    customer = session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")


def validate_menu_items_exist(session: Session, item_ids: list[int]):
    for item_id in item_ids:
        menu_item = session.get(MenuItem, item_id)
        if not menu_item:
            raise HTTPException(
                status_code=404, detail=f"Menu item {item_id} not found")
