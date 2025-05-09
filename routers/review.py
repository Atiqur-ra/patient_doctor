from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Review, Appointment, User
from schemas import ReviewCreate, ReviewOut
from database import get_db
from auth import get_current_patient


router = APIRouter()
@router.post("/reviews/", response_model=ReviewOut)
def create_review(review: ReviewCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_patient)):
    appointment = db.query(Appointment).filter_by(id=review.appointment_id, patient_id=current_user.id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found or unauthorized")

    new_review = Review(
        doctor_id=appointment.doctor_id,
        patient_id=current_user.id,
        appointment_id=appointment.id,
        rating=review.rating,
        comment=review.comment
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review
