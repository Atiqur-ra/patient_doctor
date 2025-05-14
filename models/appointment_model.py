from database import Base
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Date, Time
from sqlalchemy.orm import relationship


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"))
    doctor_id = Column(Integer, ForeignKey("users.id"))
    appointment_time = Column(DateTime, nullable=False)
    status = Column(String, default="scheduled") 

    patient = relationship("User", foreign_keys=[patient_id])
    doctor = relationship("User", foreign_keys=[doctor_id])
    documents = relationship("Document", back_populates="appointment")
    prescription = relationship("Prescription", back_populates="appointment",uselist=False)
    slot = relationship("AppointmentSlot", back_populates="appointment")


class DoctorAvailability(Base):
    __tablename__ = "doctor_availabilities"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date, nullable=False)  # Specify the date of availability
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    doctor = relationship("User")
    slots = relationship("AppointmentSlot", back_populates="availability", cascade="all, delete")

class AppointmentSlot(Base):
    __tablename__ = "appointment_slots"

    id = Column(Integer, primary_key=True, index=True)
    availability_id = Column(Integer, ForeignKey("doctor_availabilities.id"))
    slot_time = Column(Time, nullable=False)
    status = Column(String, default="available")
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)

    availability = relationship("DoctorAvailability", back_populates="slots")
    appointment = relationship("Appointment", back_populates="slot")
