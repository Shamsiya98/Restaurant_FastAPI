from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select, func
from datetime import date, datetime
from typing import List, Optional

from app.database import get_session
from app.models import *
from app.utils.logger import logger

router = APIRouter(prefix="/summary", tags=["Order Summary"])


@router.get("/", response_model=PaginatedOrderSummary)
def get_order_summary(
    date_str: Optional[str] = Query(None, alias="date"),
    page: int = Query(1, ge=1),
    per_page: int = Query(5, ge=1, le=100),
    session: Session = Depends(get_session)
):
    try:
        target_date = datetime.strptime(
            date_str, "%Y-%m-%d").date() if date_str else date.today()
    except ValueError:
        logger.warning(f"GET /orders/summary - Invalid date: {date_str}")
        return HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    logger.info(
        f"GET /orders/summary - date={target_date}, page={page}, per_page={per_page}")

    # Base query for the orders on the given date
    base_query = select(Order).where(
        func.date(Order.created_at) == target_date)

    # Get total orders using a count query
    total_orders = session.exec(
        select(func.count()).select_from(Order).where(
            func.date(Order.created_at) == target_date)
    ).one()

    total_pages = (total_orders + per_page - 1) // per_page
    offset = (page - 1) * per_page

    # Paginated order records
    orders = session.exec(
        base_query.order_by(Order.created_at.desc()).offset(
            offset).limit(per_page)
    ).all()

    summaries = []

    for order in orders:
        customer = session.get(Customer, order.customer_id)
        items = []

        for item in order.items:
            menu_item = session.get(MenuItem, item.menu_item_id)
            items.append(ItemSummary(
                name=menu_item.name,
                quantity=item.quantity,
                price=menu_item.price,
                total=round(item.quantity * menu_item.price, 2)
            ))

        summaries.append(OrderSummary(
            customer_id=customer.id,
            customer_name=customer.name,
            items_ordered=items
        ))

    logger.info(
        f"GET /orders/summary - {len(summaries)} orders retrieved for {target_date}")

    return PaginatedOrderSummary(
        date=target_date.strftime("%Y-%m-%d"),
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        total_orders=total_orders,
        orders=summaries
    )
