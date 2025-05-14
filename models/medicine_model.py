from database import Base
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey



class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    


class DispensedMedicine(Base):
    __tablename__ = "dispensed_medicines"

    id = Column(Integer, primary_key=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"))
    dispensed_by_id = Column(Integer, ForeignKey("users.id"))
    dispensed_at = Column(DateTime, default=datetime.utcnow)
    billing_amount = Column(Float)

    prescription = relationship("Prescription")
    dispensed_by = relationship("User")



class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"))
    medicine_id = Column(Integer, ForeignKey("medicines.id"))
    quantity = Column(Integer)
    billed_by = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)

    patient = relationship("User", foreign_keys=[patient_id])
    medicine = relationship("Medicine")
    pharmacy_staff = relationship("User", foreign_keys=[billed_by],overlaps="billed_by_user")
    billed_by_user = relationship("User", foreign_keys=[billed_by],overlaps="pharmacy_staff")



class Billing(Base):
    __tablename__ = "billings"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"))
    pharmacy_staff_id = Column(Integer, ForeignKey("users.id"))
    total_price = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    patient = relationship("User", foreign_keys=[patient_id])
    pharmacy_staff = relationship("User", foreign_keys=[pharmacy_staff_id])
    items = relationship("BillingItem", back_populates="billing")

class BillingItem(Base):
    __tablename__ = "billing_items"
    id = Column(Integer, primary_key=True, index=True)
    billing_id = Column(Integer, ForeignKey("billings.id"))
    medicine_id = Column(Integer, ForeignKey("medicines.id"))
    quantity = Column(Integer)
    price_per_unit = Column(Float)

    billing = relationship("Billing", back_populates="items")
    medicine = relationship("Medicine")



class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    user = relationship("User", back_populates="patient")


class MedicineImage(Base):
    __tablename__ = "medicine_images"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    extracted_text = Column(Text)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", foreign_keys=[uploaded_by])


class PatientPurchase(Base):
    __tablename__ = "patient_purchases"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("users.id"))
    total_amount = Column(Float)
    purchased_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("PurchaseItem", back_populates="purchase")


class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id = Column(Integer, primary_key=True)
    purchase_id = Column(Integer, ForeignKey("patient_purchases.id"))
    medicine_id = Column(Integer, ForeignKey("medicines.id"))
    quantity = Column(Integer)
    price = Column(Float)

    purchase = relationship("PatientPurchase", back_populates="items")
    medicine = relationship("Medicine")
