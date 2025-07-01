from sqlmodel import Session, select
import asyncio
# for async sleeps

from app.database import engine
# connects to db
from app.models import Order, MenuItem
from app.utils.logger import logger


# defines the bg task what should do
async def update_order_status(_, order_id: int):
    logger.info(f"ARQ: Received order_id={order_id}")

    with Session(engine) as session:
        order = session.exec(select(Order).where(Order.id == order_id)).first()
        if not order:
            logger.warning(f"ARQ: Order {order_id} not found")
            return

        # Step 1: Change status to "Preparing" after 1 minute
        await asyncio.sleep(60)
        order.status = "Preparing"
        session.add(order)
        session.commit()
        logger.info(f"ARQ: Order {order_id} is preparing")

        # Step 2: Fetch prep time and sleep again
        prep_times = []
        for item in order.items:
            menu_item = session.get(MenuItem, item.menu_item_id)
            if menu_item and menu_item.preparation_time_minutes:
                prep_times.append(menu_item.preparation_time_minutes)

        if prep_times:
            await asyncio.sleep(max(prep_times) * 60)

        order.status = "Completed"
        session.add(order)
        session.commit()
        logger.info(f"ARQ: Order {order_id} has been Completed")
