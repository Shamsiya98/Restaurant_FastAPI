from fastapi import APIRouter, HTTPException, Depends
# fastAPI tools
# APIRouter: to create a group of related routes (like all menu-related routes)
# HTTPException: to return custom errors (like 404 if item not found)
# Depends: to inject dependencies (like DB sessions)
from sqlmodel import Session, select
# SQLModel query tools
# Session: The DB session to run queries
# select: Used to query the database
from typing import List
# to get lists

from app.database import get_session
# Get the DB session function
from app.models import MenuItem, MenuItemCreate, MenuItemRead, MenuItemUpdate
from app.utils.validators import check_menuitem_unique_name
from app.utils.logger import logger

router = APIRouter(prefix="/menu", tags=["Menu Items"])
# tags help group routes in the API docs (Swagger UI)


# CREATE
@router.post("/", response_model=MenuItemRead)
# response_model: after creating, Returns readable items (with IDs)
def create_menu_item(
        item: MenuItemCreate,
        session: Session = Depends(get_session)):
    # item is an object of type MenuItemCreate, subclass of MenuItem
    # session: parameter
    # Session: expected type of the parameter. It's a SQLModel session class
    # Depends(get_session): Call the get_session function and give the result
    logger.info("POST/menu - Creating new menu item")

    try:
        # Unique name check
        check_menuitem_unique_name(session, item.name)

        menu_item = MenuItem(**item.model_dump())
        # .model_dump() converts the item object into a Python dict
        session.add(menu_item)
        session.commit()
        session.refresh(menu_item)
        # Reloads from DB (to get auto-generated ID)
        logger.info(f"POST/menu - Created menu item {menu_item.id}")
        return menu_item

    except Exception as e:
        logger.error(f"POST/menu - Failed to create menu item: {str(e)}")
        raise


# READ ALL
@router.get("/", response_model=List[MenuItemRead])
def get_all_menu_items(session: Session = Depends(get_session)):
    logger.info("GET/menu - Fetching all menu items")
    items = session.exec(select(MenuItem)).all()
    # select(MenuItem): SQLModel way to get all items
    # .all(): Get all results as a list
    logger.info(f"GET/menu - {len(items)} menu items retrieved")
    return items


# READ ONE
@router.get("/{item_id}", response_model=MenuItemRead)
def get_menu_item(item_id: int, session: Session = Depends(get_session)):
    logger.info(f"GET/menu/{item_id} - Fetching menu item details")
    item = session.get(MenuItem, item_id)
    if not item:
        logger.warning(f"GET/menu/{item_id} - Menu item not found")
        raise HTTPException(status_code=404, detail="Menu item not found")
    logger.info(f"GET/menu/{item_id} - Menu item retreived successfully")
    return item


# UPDATE
@router.put("/{item_id}", response_model=MenuItemRead)
def update_menu_item(
        item_id: int, updated_data: MenuItemCreate,
        session: Session = Depends(get_session)):
    logger.info(f"PUT/menu/{item_id} - Updating menu item")
    item = session.get(MenuItem, item_id)
    if not item:
        logger.warning(f"PUT/menu/{item_id} - Menu item not found")
        raise HTTPException(status_code=404, detail="Menu item not found")

    check_menuitem_unique_name(session, updated_data.name, item_id=item_id)

    for key, value in updated_data.model_dump().items():
        # .items() gives you a list of key-value pairs
        setattr(item, key, value)
        # sets the attribute on the item object
        # setattr(item, "name", "Pizza"), setattr(item, "price", 8.99) etc
        # Same as writing:
        # eg., item.name = "Pizza" , item.price = 8.99 etc

    session.add(item)
    session.commit()
    session.refresh(item)
    logger.info(f"PUT/menu/{item_id} - Menu item updated successfully")
    return item


# partial UPDATE
@router.patch("/{item_id}", response_model=MenuItemRead)
def patch_menu_item(
        item_id: int, updated_data: MenuItemUpdate,
        session: Session = Depends(get_session)):
    logger.info(f"PATCH/menu/{item_id} - Patching menu item")
    item = session.get(MenuItem, item_id)
    if not item:
        logger.warning(f"PATCH/menu/{item_id} - Menu item not found")
        raise HTTPException(status_code=404, detail="Menu item not found")

    update_data = updated_data.model_dump(exclude_unset=True)

    if "name" in update_data:
        check_menuitem_unique_name(
            session, update_data["name"], item_id=item_id)

    for key, value in update_data.items():
        # onset: only includes the fields that were sent in the request
        # ow, it will overwrite other values as NULL
        setattr(item, key, value)

    session.add(item)
    session.commit()
    session.refresh(item)
    logger.info(f"PATCH/menu/{item_id} - Menu item patched successfully")
    return item


# DELETE
@router.delete("/{item_id}", status_code=204)
# If the deletion is successful, return an HTTP 204 No Content response
def delete_menu_item(item_id: int, session: Session = Depends(get_session)):
    logger.info(f"DELETE/menu/{item_id} - Deleting menu item")
    item = session.get(MenuItem, item_id)
    if not item:
        logger.warning(f"DELETE/menu/{item_id} - Menu Item not found")
        raise HTTPException(status_code=404, detail="Menu item not found")

    session.delete(item)
    session.commit()
    logger.info(f"DELETE/menu/{item_id} - Menu item deleted successfully")
    return
    # Since we’re returning 204, just a blank response to say "done"
