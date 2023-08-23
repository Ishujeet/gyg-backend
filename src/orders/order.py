from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.models.base import get_db
from src.models.order import Order
from src.models.customer import Customer
from src.models.gym_slot import Gym, Slot
from datetime import datetime
from src.customer.login import get_current_user
from pydantic import BaseModel
from enum import Enum
from src.utils import generate_id

order_router = APIRouter(
    prefix="/order",
    tags=["order"],
    dependencies=[Depends(get_current_user)],
    responses={403: {"description": "Forbidden"}},
)

class Status(str, Enum):
    Created: 'Created'
    Pending: 'Pending'
    Processing: 'Processing'
    Confirmed: 'Confirmed'
    Failed: 'Failed'
    Cancelled: 'Cancelled' 

class OrderDetails(BaseModel):
    order_id: str
    customer_id: str
    gym_id: str
    slot_id: str
    order_time: datetime
    status: Status

@order_router.post("/create_order/")
def create_order(order: OrderDetails, db: Session = Depends(get_db)):
    # Validate customer
    customer = db.query(Customer).filter(Customer.customer_id == order.customer_id).first()
    if not customer:
        raise HTTPException(status_code=400, detail="Invalid customer ID")
    
    # Validate gym
    gym = db.query(Gym).filter(Gym.gym_id == order.gym_id).first()
    if not gym:
        raise HTTPException(status_code=400, detail="Invalid gym ID")
    
    # Validate slot
    slot = db.query(Slot).filter(Slot.slot_id == order.slot_id).first()
    if not slot:
        raise HTTPException(status_code=400, detail="Invalid slot ID")
    
    # Validate order time
    now = datetime.now()
    if order.order_time <= now:
        raise HTTPException(status_code=400, detail="Invalid order time")
    
    # Check if the slot is available
    if slot.available_capacity <= 0:
        raise HTTPException(status_code=400, detail="Slot not available")
    
    # Assuming other validations and checks...
    
    order.order_time = datetime.now()
    order.status = "Created"
    order.order_id = generate_id()
    db.add(order)
    db.commit()
    db.refresh(order)

    # Decrease slot capacity when an order is created
    slot = db.query(Slot).filter(Slot.slot_id == order.slot_id).first()
    if slot:
        slot.available_capacity -= 1
        db.commit()
    
    return order

@order_router.put("/update_order_status/{order_id}")
def update_order_status(order_id: int, new_status: str, db: Session = Depends(get_db)):
    allowed_statuses = ["Created", "Confirmed", "Cancelled"]
    if new_status not in allowed_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Restore slot capacity if order status changes from "Confirmed" or "Pending" to "Cancelled" or "Failed"
    if order.status in ["Created", "Confirmed", "Pending"] and new_status in ["Failed"]:
        slot = db.query(Slot).filter(Slot.slot_id == order.slot_id).first()
        if slot:
            slot.available_capacity += 1
            db.commit()
    
    order.status = new_status
    db.commit()
    
    return {"message": f"Order status updated to {new_status}"}

@order_router.put("/cancel_order/{order_id}")
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Assuming you have additional logic to check if the order can be cancelled
    
    order.status = "Cancelled"  # Update the status
    db.commit()
    
    return {"message": "Order cancelled"}