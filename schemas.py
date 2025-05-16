from pydantic import BaseModel, EmailStr, ConfigDict
from enum import Enum
from datetime import datetime
from typing import List, Optional
from models.user_model import UserRole
from datetime import time, date



class RoleEnum(str, Enum):
    patient = "patient"
    doctor = "doctor"
    pharmacy = "pharmacy"
    admin = "admin"

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: RoleEnum
    department: str | None = None

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: RoleEnum
    department: str | None

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class AppointmentCreate(BaseModel):
    doctor_id: int
    appointment_time: datetime

class AppointmentOut(BaseModel):
    id: int
    doctor_id: int
    patient_id: int
    appointment_time: datetime
    status: str

    model_config = ConfigDict(from_attributes=True)

class AvailabilityCreate(BaseModel):
    available_time: datetime

class AvailabilityOut(BaseModel):
    id: int
    doctor_id: int
    date: date
    start_time: time
    end_time: time

    model_config = ConfigDict(from_attributes=True)

class SlotInfo(BaseModel):
    slot_id: int
    slot_time: time
    status: str

class AvailabilityWithDoctorInfo(BaseModel):
    availability_id: int
    doctor_id: int
    doctor_name: str
    doctor_department: str
    date: date
    start_time: time
    end_time: time
    average_rating: Optional[float]
    slots: List[SlotInfo]

    model_config = ConfigDict(from_attributes=True)      

class DocumentOut(BaseModel):
    id: int
    filename: str
    content_type: str
    document_id: str

    model_config = ConfigDict(from_attributes=True)




class DocumentPreviewOut(BaseModel):
    id: int
    filename: str
    content_type: str
    preview_url: str

    model_config = ConfigDict(from_attributes=True)

class PatientOut(BaseModel):
    id: int
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)

class AppointmentWithDocsOut(BaseModel):
    id: int
    appointment_time: datetime
    patient: PatientOut   
    documents: List[DocumentOut] = []


    model_config = ConfigDict(from_attributes=True)


class PrescriptionCreate(BaseModel):
    patient_id: int
    issue_details: str
    medicines: str

class PrescriptionOut(BaseModel):
    id: int
    appointment_id: int
    doctor_id: int
    patient_id: int
    issue_details: str
    medicines: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReviewCreate(BaseModel):
    appointment_id: int
    comment: Optional[str] = None

class ReviewOut(BaseModel):
    id: int
    doctor_id: int
    comment: Optional[str]
    created_at: datetime


    model_config = ConfigDict(from_attributes=True)

class MedicineBase(BaseModel):
    name: str
    description: str = ""
    quantity: int
    price: float

class MedicineCreate(MedicineBase):
    pass

class MedicineUpdate(BaseModel):
    quantity: int
    price: float

class MedicineOut(MedicineBase):
    id: int


    model_config = ConfigDict(from_attributes=True)


class BillingItemCreate(BaseModel):
    medicine_id: int
    quantity: int

class BillItem(BaseModel):
    medicine_id: int
    quantity: int

class BillCreate(BaseModel):
    patient_id: int
    items: list[BillItem]


class BillMedicineItem(BaseModel):
    medicine_name: str
    quantity: int

class BillResponse(BaseModel):
    patient_name: str
    billed_by: str
    medicines: List[BillMedicineItem]
    total_amount: float


class UserUpdate(BaseModel):
    name: Optional[str]
    email: Optional[str]
    role: Optional[UserRole]


class MedicinePurchase(BaseModel):
    medicine_id: int
    quantity: int

class PurchaseRequest(BaseModel):
    patient_id: int
    medicines: List[MedicinePurchase]


class MagicLinkRequest(BaseModel):
    email: EmailStr

class MagicLinkPayload(BaseModel):
    magic_link: str 