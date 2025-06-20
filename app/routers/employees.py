from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from typing import List

from app.database import get_session
from app.models import Employee, EmployeeCreate, EmployeeRead, EmployeeUpdate
from app.utils.validators import check_employee_unique_fields
from app.utils.logger import logger

router = APIRouter(prefix="/employees", tags=["Employees"])


# CREATE
@router.post("/", response_model=EmployeeRead)
def add_employee(
        emp: EmployeeCreate,
        session: Session = Depends(get_session)
):
    try:
        logger.info("POST/employees - Adding new employee")
        check_employee_unique_fields(session, emp.email, emp.phone)
        employee = Employee(**emp.model_dump())
        session.add(employee)
        session.commit()
        session.refresh(employee)
        logger.info(f"POST/employees - Added employee {employee.name}")
        return employee

    except Exception as e:
        logger.error(f"POST/employees - Failed to add employee: {str(e)}")
        raise


# READ ALL
@router.get("/", response_model=List[EmployeeRead])
def list_employees(session: Session = Depends(get_session)):
    logger.info("GET/employees - Fetching all employees...")
    employees = session.exec(select(Employee)).all()
    logger.info(f"GEt/employees - {len(employees)} employees retrieved")
    return employees


# READ ONE
@router.get("/{emp_id}", response_model=EmployeeRead)
def get_employee(emp_id: int, session: Session = Depends(get_session)):
    logger.info(f"GET/employees/{emp_id} - Fetching employee details")
    employee = session.get(Employee, emp_id)
    if not employee:
        logger.warning(f"GET/employees/{emp_id} - Employee not found")
        raise HTTPException(status_code=404, detail="Employee item not found")
    logger.info(f"GET/employees/{emp_id} - Employee details retrieved")
    return employee


# UPDATE
@router.put("/{emp_id}", response_model=EmployeeRead)
def update_employee(
        emp_id: int, updated_data: EmployeeCreate,
        session: Session = Depends(get_session)
):
    logger.info(f"PUT/employees/{emp_id} - Updating employee details")
    employee = session.get(Employee, emp_id)
    if not employee:
        logger.warning(f"PUT/employees/{emp_id} - Employee not found")
        raise HTTPException(status_code=404, detail="Employee not found")

    # Check if email or phone is already taken by another employee
    check_employee_unique_fields(session,
                                 updated_data.email,
                                 updated_data.phone,
                                 emp_id=emp_id)

    for key, value in updated_data.model_dump().items():
        setattr(employee, key, value)

    session.add(employee)
    session.commit()
    session.refresh(employee)
    logger.info(f"PUT/employees/{emp_id} - Employee updated successfully")
    return employee


# partial UPDATE
@router.patch("/{emp_id}", response_model=EmployeeRead)
def patch_employee(
        emp_id: int, updated_data: EmployeeUpdate,
        session: Session = Depends(get_session)
):
    logger.info(f"PATCH/employees/{emp_id} - Patching employee details")
    employee = session.get(Employee, emp_id)
    if not employee:
        logger.warning(f"PATCH/employees/{emp_id} - Employee not found")
        raise HTTPException(status_code=404, detail="Employee not found")

    update_data = updated_data.model_dump(exclude_unset=True)

    # Unique check for email and phone if present
    email = update_data.get("email")
    phone = update_data.get("phone")
    if email or phone:
        check_employee_unique_fields(session, email, phone, emp_id=emp_id)

    for key, value in update_data.items():
        setattr(employee, key, value)

    session.add(employee)
    session.commit()
    session.refresh(employee)
    logger.info(f"PATCH/employees/{emp_id} - Employee patched successfully")
    return employee


# DELETE
@router.delete("/{emp_id}", status_code=204)
def delete_employee(emp_id: int, session: Session = Depends(get_session)):
    logger.info(f"DELETE/employees/{emp_id} - Deleting employee")
    employee = session.get(Employee, emp_id)
    if not employee:
        logger.warning(f"DELETE/employees/{emp_id} - Employee not found")
        raise HTTPException(status_code=404, detail="Employee not found")

    session.delete(employee)
    session.commit()
    logger.info(f"DELETE/employees/{emp_id} - Employee deleted successfully")
    return
