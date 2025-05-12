from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user_model import  User
from models.appointment_model import DoctorAvailability
from schemas import AvailabilityCreate, AvailabilityOut
from utils.security import get_current_user

router = APIRouter(prefix="/availability", tags=["Availability"])

@router.post("/", response_model=AvailabilityOut)
def set_availability(
    data: AvailabilityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can set availability")

    availability = DoctorAvailability(doctor_id=current_user.id, available_time=data.available_time)
    db.add(availability)
    db.commit()
    db.refresh(availability)
    return availability

@router.get("/", response_model=list[AvailabilityOut])
def list_all_availability(db: Session = Depends(get_db)):
    return db.query(DoctorAvailability).all()
