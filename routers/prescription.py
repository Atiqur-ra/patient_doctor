from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.appointment_model import Appointment
from models.prescription_model import Prescription
from schemas import PrescriptionCreate, PrescriptionOut
from database import get_db
from auth import get_current_doctor
from models.user_model import User
from typing import List
from auth import get_current_patient


router = APIRouter(prefix="/api", tags=["Prescriptions"])

@router.post("/prescriptions/", response_model=PrescriptionOut)
def create_prescription(prescription: PrescriptionCreate, db: Session = Depends(get_db), current_doctor: User = Depends(get_current_doctor)):
    appointment = db.query(Appointment).filter(
        Appointment.patient_id == prescription.patient_id,
        Appointment.doctor_id == current_doctor['id'],
    ).first()

    if not appointment:
        raise HTTPException(status_code=403, detail="No appointment found with this patient for the current doctor.")

    new_prescription = Prescription(
        appointment_id=appointment.id,
        doctor_id=current_doctor['id'],
        patient_id=prescription.patient_id,
        issue_details=prescription.issue_details,
        medicines=prescription.medicines
    )
    db.add(new_prescription)
    db.commit()
    return new_prescription

@router.get("/prescriptions-patient/", response_model=List[PrescriptionOut])
def get_prescriptions_for_patient(db: Session = Depends(get_db), current_user: User = Depends(get_current_patient)):
    return db.query(Prescription).filter_by(patient_id=current_user['id']).all()

