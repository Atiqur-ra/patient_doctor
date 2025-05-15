from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user_model import User
from models.appointment_model import Appointment, DoctorAvailability
from schemas import  AppointmentOut,AppointmentWithDocsOut
from models.appointment_model import AppointmentSlot
from datetime import datetime
import os
from models.documents_model import Document
from uuid import uuid4
from fastapi import File, UploadFile, Form
from auth import get_current_patient, get_current_doctor
from typing import List, Optional
from fastapi import Request
from schemas import DocumentOut, PatientOut

router = APIRouter(prefix="/appointments", tags=["Appointments"])

UPLOAD_DIR = "uploaded_documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)



@router.post("/book", response_model=AppointmentOut)
def book_appointment(
    doctor_id: int = Form(...),
    slot_id: int = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    slot = (
        db.query(AppointmentSlot)
        .join(AppointmentSlot.availability)
        .filter(
            AppointmentSlot.id == slot_id,
            AppointmentSlot.status == "available",
            DoctorAvailability.id == AppointmentSlot.availability_id,
            DoctorAvailability.doctor_id == doctor_id,
            DoctorAvailability.date >= datetime.now().date()
            
        )
        .first()
    )
  
    if not slot:
        raise HTTPException(
            status_code=400,
            detail="Invalid slot ID or this slot is not available for the selected doctor."
        )
    

    availability = slot.availability
    appointment_time = datetime.combine(availability.date, slot.slot_time)
    if appointment_time < datetime.now():
        raise HTTPException(
            status_code=400,
            detail="You cannot book an appointment for a past date."
        )


    appointment = Appointment(
        doctor_id=doctor_id,
        patient_id=current_user['id'],
        appointment_time=appointment_time
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)


    slot.status = "booked"
    slot.appointment_id = appointment.id
    db.commit()

    if files:
        for file in files:
            if file.filename:
                ext = file.filename.split(".")[-1]
                unique_name = f"{uuid4()}.{ext}"
                path = os.path.join(UPLOAD_DIR, unique_name)

                with open(path, "wb") as buffer:
                    buffer.write(file.file.read())

                document = Document(
                    filename=file.filename,
                    content_type=file.content_type,
                    path=path,
                    uploaded_by_id=current_user['id'],
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
    appointments = (
        db.query(Appointment)
        .filter(Appointment.doctor_id == current_doctor['id'])
        .all()
    )

    response = []

    for appointment in appointments:
        patient = appointment.patient

        documents_out = [
            DocumentOut(
                id=doc.id,
                filename=doc.filename,
                content_type=doc.content_type,
                document_id=f"{doc.id}"
            )
            for doc in appointment.documents
        ]

        response.append(AppointmentWithDocsOut(
            id=appointment.id,
            appointment_time=appointment.appointment_time,
            patient=PatientOut(
                id=patient.id,
                name=patient.name,
                email=patient.email
            ),
            documents=documents_out
        ))

    return response


