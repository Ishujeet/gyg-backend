from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, CheckConstraint
from sqlalchemy.orm import relationship
from .base import Base



class Order(Base):
    __tablename__ = 'order'
    order_id = Column(String(50), primary_key=True)
    customer_id = Column(String(50), ForeignKey('customer.customer_id'))
    gym_id = Column(String(50), ForeignKey('gym.gym_id'))
    slot_id = Column(String(50), ForeignKey('slot.slot_id'))
    order_time = Column(DateTime)
    status = Column(String(20), CheckConstraint("status IN ('Created','Pending','Processing','Confirmed','Failed','Cancelled')"))

    customer = relationship("Customer", back_populates="orders")
    gym = relationship("Gym", back_populates="orders")
    slot = relationship("Slot", back_populates="orders")
