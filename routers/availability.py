from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user_model import  User
from models.appointment_model import DoctorAvailability
from schemas import AvailabilityCreate, AvailabilityOut
from auth import get_current_doctor
from models.appointment_model import AppointmentSlot
from datetime import date, time, datetime
from fastapi import Form

router = APIRouter(prefix="/availability", tags=["Availability"])

@router.post("/set_availability", response_model=AvailabilityOut)
def set_availability(
    date: date = Form(...),
    start_time: time = Form(...),
    end_time: time = Form(...),
    current_user: User = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):
    availability = DoctorAvailability(
        doctor_id=current_user.id,
        date=date,
        start_time=start_time,
        end_time=end_time
    )
    db.add(availability)
    db.commit()

    # Generate 10 equal time slots
    start_dt = datetime.combine(date, start_time)
    end_dt = datetime.combine(date, end_time)
    total_duration = (end_dt - start_dt) / 10

    for i in range(10):
        slot_time = (start_dt + i * total_duration).time()
        slot = AppointmentSlot(availability_id=availability.id, slot_time=slot_time)
        db.add(slot)

    db.commit()
    return availability


