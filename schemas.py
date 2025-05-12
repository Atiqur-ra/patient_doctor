from pydantic import BaseModel, EmailStr
from enum import Enum
from datetime import datetime
from typing import List, Optional
from models import UserRole
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
    department: str | None = None  # Optional unless role is doctor

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: RoleEnum
    department: str | None

    class Config:
        orm_mode = True

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

    class Config:
        orm_mode = True

class AvailabilityCreate(BaseModel):
    available_time: datetime

class AvailabilityOut(BaseModel):
    id: int
    doctor_id: int
    available_time: datetime

    class Config:
        orm_mode = True

class DocumentOut(BaseModel):
    id: int
    filename: str
    content_type: str
    path: str

    class Config:
        orm_mode = True

class DocumentOut(BaseModel):
    id: int
    filename: str
    content_type: str
    path: str
    download_url: Optional[str] = None

    class Config:
        orm_mode = True


class DocumentPreviewOut(BaseModel):
    id: int
    filename: str
    content_type: str
    preview_url: str
    class Config:
        orm_mode = True

class PatientOut(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        orm_mode = True

class AppointmentWithDocsOut(BaseModel):
    id: int
    appointment_time: datetime
    patient: PatientOut   
    documents: List[DocumentOut] = []

    class Config:
        orm_mode = True

class PatientOut(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        orm_mode = True

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

    class Config:
        orm_mode = True


class ReviewCreate(BaseModel):
    appointment_id: int
    comment: Optional[str] = None

class ReviewOut(BaseModel):
    id: int
    doctor_id: int
    comment: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True

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

    class Config:
        orm_mode = True


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