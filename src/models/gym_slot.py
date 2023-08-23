from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from .base import Base


class Gym(Base):
    __tablename__ = 'gym'
    gym_id = Column(String(50), primary_key=True)
    name = Column(String(100))
    address = Column(String(200))
    capacity = Column(Integer)
    owner_id = Column(String(50), ForeignKey('gym_owner.owner_id'))
    status = Column(String(20), CheckConstraint("status IN ('Added', 'Paused', 'Stopped')"))
    
    owner = relationship("GymOwner", back_populates="gyms")
    slots = relationship("Slot", back_populates="gym")
    orders = relationship("Order", back_populates="gym")

class Slot(Base):
    __tablename__ = 'slot'
    slot_id = Column(String(50), primary_key=True)
    gym_id = Column(String(50), ForeignKey('gym.gym_id'))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    available_capacity = Column(Integer)
    
    gym = relationship("Gym", back_populates="slots")
    orders = relationship("Order", back_populates="slot")
