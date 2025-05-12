from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user_model import User
from models.appointment_model import Appointment
from schemas import  AppointmentOut,AppointmentWithDocsOut
from datetime import datetime
import os
from models.documents_model import Document
from uuid import uuid4
from fastapi import File, UploadFile, Form
from auth import get_current_patient, get_current_doctor
from typing import List
from fastapi import Request
from sqlalchemy import func

router = APIRouter(prefix="/appointments", tags=["Appointments"])

UPLOAD_DIR = "uploaded_documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/book/", response_model=AppointmentOut)
def book_appointment(
    doctor_id: int = Form(...),
    scheduled_time: datetime = Form(...),
    file: UploadFile = File(None),
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
     # Extract date from datetime
    appointment_date = scheduled_time.date()

    # Count existing appointments for this doctor on the same date
    count = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        func.date(Appointment.appointment_time) == appointment_date
    ).count()

    if count >= 20:
        raise HTTPException(status_code=400, detail="Booking limit for this doctor on this date is full")


    appointment = Appointment(
        doctor_id=doctor_id,
        patient_id=current_user.id,
        appointment_time=scheduled_time
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    if file:
        ext = file.filename.split(".")[-1]
        unique_name = f"{uuid4()}.{ext}"
        path = os.path.join(UPLOAD_DIR, unique_name)

        with open(path, "wb") as buffer:
            buffer.write(file.file.read())

        document = Document(
            filename=file.filename,
            content_type=file.content_type,
            path=path,
            uploaded_by_id=current_user.id,
            appointment_id=appointment.id
        )
        db.add(document)
        db.commit()

    return appointment



@router.get("/doctor/view", response_model=List[AppointmentWithDocsOut])
def view_appointments_for_doctor(
    request: Request,
    db: Session = Depends(get_db),
    current_doctor: User = Depends(get_current_doctor)
):
    appointments = db.query(Appointment).filter(Appointment.doctor_id == current_doctor.id).all()
    
    # Inject download URL into each document
    for appointment in appointments:
        for doc in appointment.documents:
            doc.download_url = f"{request.base_url}documents/download/{doc.id}"

    return appointments

