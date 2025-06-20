# Makes 'models' a Python package
# Without this we can't import models, raises error Module Not Found
from .menu import *
from .employees import *
from .customers import *
from .orders import *
from .order_items import *


__all__ = [
    "MenuItem", "MenuItemCreate", "MenuItemRead", "MenuItemUpdate",
    "Employee", "EmployeeCreate", "EmployeeRead", "EmployeeUpdate",
    "Customer", "CustomerCreate", "CustomerRead", "CustomerUpdate",
    "Order", "OrderCreate", "OrderRead", "OrderUpdate",
    "OrderItem", "OrderItemCreate", "MenuItemNested", "OrderItemRead"
]

# Rebuild Pydantic models with forward references
Customer.model_rebuild()
MenuItem.model_rebuild()
Order.model_rebuild()
OrderCreate.model_rebuild()
OrderRead.model_rebuild()
OrderUpdate.model_rebuild()
OrderItem.model_rebuild()
OrderItemCreate.model_rebuild()
OrderItemRead.model_rebuild()
