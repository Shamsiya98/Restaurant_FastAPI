from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from typing import List
from sqlmodel import delete
from fastapi import BackgroundTasks

from app.database import get_session
from app.models import *
from app.utils.validators import validate_customer_exists, validate_menu_items_exist
from app.utils.logger import logger
from app.tasks.enqueue import enqueue_sync


router = APIRouter(prefix="/orders", tags=["Orders"])


# CREATE
@router.post("/", response_model=OrderRead)
def create_order(
        order: OrderCreate,
        background_tasks: BackgroundTasks,
        session: Session = Depends(get_session)
):
    # BackgroundTasks run small bg tasks after sending response to client, no blocking
    logger.info("POST/order - Creating new order")

    try:
        validate_customer_exists(session, order.customer_id)
        item_ids = [item.menu_item_id for item in order.items]
        validate_menu_items_exist(session, item_ids)

        new_order = Order(customer_id=order.customer_id, status=order.status)

        # Attach OrderItems (as model instances, not dicts)
        new_order.items = [
            OrderItem(menu_item_id=item.menu_item_id, quantity=item.quantity)
            for item in order.items
        ]

        session.add(new_order)
        session.commit()
        session.refresh(new_order)
        logger.info(
            f"POST/order - Order {new_order.id} created with {len(order.items)} items")

        # Enqueue background task
        background_tasks.add_task(enqueue_sync, new_order.id)

        return new_order

    except Exception as e:
        logger.error(f"POST/order - Failed to create order: {str(e)}")
        raise


# READ ALL
@router.get("/", response_model=List[OrderRead])
def list_orders(session: Session = Depends(get_session)):
    logger.info("GET/order - Fetching all orders...")
    orders = session.exec(select(Order)).all()
    logger.info(f"GET/order - {len(orders)} orders retrieved")
    return orders


# READ ONE
@router.get("/{order_id}", response_model=OrderRead)
def get_order(order_id: int, session: Session = Depends(get_session)):
    logger.info(f"GET/order/{order_id} - Fetching order details")
    order = session.get(Order, order_id)
    if not order:
        logger.warning(f"GET/order/{order_id} - Order not found")
        raise HTTPException(status_code=404, detail="Order not found")
    logger.info(f"GET/order/{order_id} - Order retrieved successfully")
    return order


# UPDATE
@router.put("/{order_id}", response_model=OrderRead)
def update_order(
        order_id: int,
        updated_data: OrderCreate,
        session: Session = Depends(get_session)
):
    logger.info(f"PUT/order/{order_id} - Updating order")
    order = session.get(Order, order_id)
    if not order:
        logger.warning(f"PUT/order/{order_id} - Order not found")
        raise HTTPException(status_code=404, detail="Order not found")

    validate_customer_exists(session, updated_data.customer_id)
    item_ids = [item.menu_item_id for item in updated_data.items]
    validate_menu_items_exist(session, item_ids)

    order.customer_id = updated_data.customer_id
    order.status = updated_data.status

    # Delete old items
    session.exec(delete(OrderItem).where(OrderItem.order_id == order_id))
    session.commit()

    # Add new order items
    order.items = [
        OrderItem(menu_item_id=item.menu_item_id, quantity=item.quantity)
        for item in updated_data.items
    ]

    session.add(order)
    session.commit()
    session.refresh(order)
    logger.info(
        f"PUT/order/{order_id} - Order updated successfully with {len(order.items)} items")
    return order


# partial UPDATE
@router.patch("/{order_id}", response_model=OrderRead)
def patch_order(
        order_id: int,
        updated_data: OrderUpdate,
        session: Session = Depends(get_session)
):
    logger.info(f"PATCH/order/{order_id} - Patching order")
    order = session.get(Order, order_id)
    if not order:
        logger.warning(f"PATCH/order/{order_id} - Order not found")
        raise HTTPException(status_code=404, detail="Order not found")

    update_data = updated_data.model_dump(exclude_unset=True)

    if "customer_id" in update_data:
        validate_customer_exists(session, update_data["customer_id"])
        order.customer_id = update_data["customer_id"]

    if "status" in update_data:
        order.status = update_data["status"]

    session.commit()
    session.refresh(order)
    logger.info(f"PATCH/order/{order_id} - Order patched successfully")
    return order


# DELETE
@router.delete("/{order_id}", status_code=204)
def delete_order(order_id: int, session: Session = Depends(get_session)):
    logger.info(f"DELETE/order/{order_id} - Deleting order")
    order = session.get(Order, order_id)
    if not order:
        logger.warning(f"PATCH/order/{order_id} - Order not found")
        raise HTTPException(status_code=404, detail="Order not found")

    session.delete(order)
    session.commit()
    logger.info(f"PATCH/order/{order_id} - Order deleted successfully")
    return
