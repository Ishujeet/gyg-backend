from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base



class Order(Base):
    __tablename__ = 'order'
    order_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customer.customer_id'))
    gym_id = Column(Integer, ForeignKey('gym.gym_id'))
    slot_id = Column(Integer, ForeignKey('slot.slot_id'))
    order_time = Column(DateTime)
    
    customer = relationship("Customer", back_populates="orders")
    gym = relationship("Gym", back_populates="orders")
    slot = relationship("Slot", back_populates="orders")
