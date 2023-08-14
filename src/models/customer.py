from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base

class Customer(Base):
    __tablename__ = 'customer'
    customer_id = Column(Integer, primary_key=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(100))
    phone_number = Column(String(20))
    
    orders = relationship("Order", back_populates="customer")

class LoginCredential(Base):
    __tablename__ = 'login_credential'
    credential_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, unique=True)
    username = Column(String(50), unique=True)
    password = Column(String(100))
    registration_date = Column(DateTime)
