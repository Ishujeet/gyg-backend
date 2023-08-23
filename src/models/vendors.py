from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.models.base import Base
import bcrypt


class GymOwner(Base):
    __tablename__ = 'gym_owner'
    owner_id = Column(String(50), primary_key=True)
    username = Column(String(50), unique=True)
    password = Column(String(100))
    
    gyms = relationship("Gym", back_populates="owner", lazy="dynamic")

    def set_password(self, password):
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
