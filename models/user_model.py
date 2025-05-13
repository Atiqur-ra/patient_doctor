from database import Base
import enum
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import Column, String, Enum, Integer
from pydantic import BaseModel

class UserRole(str, enum.Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    PHARMACY = "pharmacy"
    ADMIN = "admin"



class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    department = Column(String, nullable=True) 
    availabilities = relationship("DoctorAvailability", back_populates="doctor")
    patient = relationship("Patient", back_populates="user", uselist=False)

