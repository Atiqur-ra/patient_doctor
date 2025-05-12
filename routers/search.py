from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from models.user_model import User
from models.appointment_model import DoctorAvailability
from schemas import AvailabilityOut
from typing import List

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("/doctors/", response_model=List[AvailabilityOut])
def search_doctors(
    name: str = Query(None),
    department: str = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(User).filter(User.role == "doctor")
    
    if name:
        query = query.filter(User.name.ilike(f"%{name}%"))
    if department:
        query = query.filter(User.department.ilike(f"%{department}%"))

    doctors = query.all()

    doctor_ids = [doc.id for doc in doctors]

    availability = db.query(DoctorAvailability).filter(
        DoctorAvailability.doctor_id.in_(doctor_ids)
    ).all()

    return availability
