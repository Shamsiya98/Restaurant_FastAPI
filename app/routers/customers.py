from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from typing import List

from app.database import get_session
from app.models import Customer, CustomerCreate, CustomerRead, CustomerUpdate
from app.utils.validators import check_customer_unique_email
from app.utils.logger import logger

router = APIRouter(prefix="/customers", tags=["Customers"])


# CREATE
@router.post("/", response_model=CustomerRead)
def add_customer(
        customer: CustomerCreate,
        session: Session = Depends(get_session)
):
    try:
        logger.info("POST/customers/ - Adding new customer...")

        check_customer_unique_email(session, customer.email)
        customer = Customer(**customer.model_dump())
        session.add(customer)
        session.commit()
        session.refresh(customer)
        return customer

    except Exception as e:
        logger.error(f"POST/customers - Failed to add customer: {str(e)}")
        raise


# READ ALL
@router.get("/", response_model=List[CustomerRead])
def list_customers(session: Session = Depends(get_session)):
    logger.info("GET/customers - Fetching all customers")
    customers = session.exec(select(Customer)).all()
    logger.info(f"GET/customers - {len(customers)} customers retrieved")
    return customers


# READ ONE
@router.get("/{customer_id}", response_model=CustomerRead)
def get_customer(customer_id: int, session: Session = Depends(get_session)):
    logger.info(f"POST/customers/{customer_id} - Fetching customer details")
    customer = session.get(Customer, customer_id)
    if not customer:
        logger.warning(f"POST/customers/{customer_id} - Customer not found")
        raise HTTPException(status_code=404, detail="Customer not found")
    logger.info(f"POST/customers/{customer_id} - Customer details retrieved")
    return customer


# UPDATE
@router.put("/{customer_id}", response_model=CustomerRead)
def update_customer(
        customer_id: int, updated_data: CustomerCreate,
        session: Session = Depends(get_session)
):
    logger.info(f"POST/customers/{customer_id} - Updating customer details")
    customer = session.get(Customer, customer_id)
    if not customer:
        logger.warning(f"POST/customers/{customer_id} - Customer not found")
        raise HTTPException(status_code=404, detail="Customer not found")

    # Check if email or phone is already taken by another employee
    check_customer_unique_email(session,
                                updated_data.email,
                                customer_id=customer_id)

    for key, value in updated_data.model_dump().items():
        setattr(customer, key, value)

    session.add(customer)
    session.commit()
    session.refresh(customer)
    logger.info(f"POST/customers/{customer_id} - Customer details updated")
    return customer


# partial UPDATE
@router.patch("/{customer_id}", response_model=CustomerRead)
def patch_customer(
        customer_id: int, updated_data: CustomerUpdate,
        session: Session = Depends(get_session)
):
    logger.info(f"PATCH/customers/{customer_id} - Patching customer details")
    customer = session.get(Customer, customer_id)
    if not customer:
        logger.warning(f"PATCH/customers/{customer_id} - Customer not found")
        raise HTTPException(status_code=404, detail="Customer not found")

    update_data = updated_data.model_dump(exclude_unset=True)

    # Unique check for email and phone if present
    email = update_data.get("email")
    if email:
        check_customer_unique_email(session, email, customer_id=customer_id)

    for key, value in update_data.items():
        setattr(customer, key, value)

    session.add(customer)
    session.commit()
    session.refresh(customer)
    logger.info(f"PATCH/customers/{customer_id} - Customer details patched")
    return customer


# DELETE
@router.delete("/{customer_id}", status_code=204)
def delete_customer(customer_id: int, session: Session = Depends(get_session)):
    logger.info(f"DELETE/customers/{customer_id} - Deleting customer")
    customer = session.get(Customer, customer_id)
    if not customer_id:
        logger.warning(f"DELETE/customers/{customer_id} - Customer not found")
        raise HTTPException(status_code=404, detail="Customer not found")

    session.delete(customer)
    session.commit()
    logger.info(f"DELETE/customers/{customer_id} - Customer deleted")
    return
