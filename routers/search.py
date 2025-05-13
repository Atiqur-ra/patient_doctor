from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from models.user_model import User
from models.appointment_model import DoctorAvailability
from schemas import AvailabilityWithDoctorInfo
from typing import List
from models.reviews_model import Review

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("/doctors/", response_model=List[AvailabilityWithDoctorInfo])
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

    availabilities = (
        db.query(DoctorAvailability)
        .filter(DoctorAvailability.doctor_id.in_(doctor_ids))
        .all()
    )

    result = []
    for a in availabilities:
        doctor = next((doc for doc in doctors if doc.id == a.doctor_id), None)

        # Calculate average rating from Review table
        review_query = db.query(Review).filter(Review.doctor_id == a.doctor_id).all()
        avg_rating = None
        if review_query:
            total = sum([r.rating for r in review_query])
            avg_rating = round(total / len(review_query), 2)

        result.append(AvailabilityWithDoctorInfo(
            id=a.id,
            doctor_id=a.doctor_id,
            available_time=a.available_time,
            doctor_name=doctor.name if doctor else "Unknown",
            doctor_rating=avg_rating
        ))

    return result

