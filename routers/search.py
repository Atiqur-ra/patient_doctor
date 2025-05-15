from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user_model import User
from models.appointment_model import DoctorAvailability
from schemas import AvailabilityWithDoctorInfo, SlotInfo
from typing import List
from models.reviews_model import Review
from auth import get_current_patient
from models.appointment_model import AppointmentSlot

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("/search-doctors", response_model=List[AvailabilityWithDoctorInfo])
def search_doctors(
    name: str = Query(None),
    department: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient)
):


    query = db.query(User).filter(User.role == "doctor")
    if name:
        query = query.filter(User.name.ilike(f"%{name}%"))
    if department:
        query = query.filter(User.department.ilike(f"%{department}%"))

    doctors = query.all()
    doctor_ids = [doc.id for doc in doctors]


    availabilities = (
        db.query(DoctorAvailability)
        .filter(DoctorAvailability.doctor_id.in_(doctor_ids))
        .all()
    )

    result = []

    for availability in availabilities:
        doctor = next((doc for doc in doctors if doc.id == availability.doctor_id), None)

     
        reviews = db.query(Review).filter(Review.doctor_id == availability.doctor_id).all()
        avg_rating = round(sum([r.rating for r in reviews]) / len(reviews), 2) if reviews else None

        slots = (
            db.query(AppointmentSlot)
            .filter(AppointmentSlot.availability_id == availability.id)
            .order_by(AppointmentSlot.slot_time)
            .all()
        )

        slot_out = [
            SlotInfo(
            slot_id=slot.id,
            slot_time=slot.slot_time,
            status=slot.status
            )
        for slot in slots
        ]

        result.append(AvailabilityWithDoctorInfo(
            availability_id=availability.id,
            doctor_id=availability.doctor_id,
            doctor_name=doctor.name,
            doctor_department=doctor.department,
            date=availability.date,
            start_time=availability.start_time,
            end_time=availability.end_time,
            average_rating=avg_rating,
            slots=slot_out
            ))
            

    return result
