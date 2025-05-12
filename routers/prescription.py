from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Appointment, Prescription
from schemas import PrescriptionCreate, PrescriptionOut
from database import get_db
from auth import get_current_doctor
from models import User
from typing import List
from auth import get_current_patient
from auth import get_current_user
from models import DispensedMedicine

router = APIRouter()

@router.post("/prescriptions/", response_model=PrescriptionOut)
def create_prescription(prescription: PrescriptionCreate, db: Session = Depends(get_db), current_doctor: User = Depends(get_current_doctor)):
    appointment = db.query(Appointment).filter(
        Appointment.patient_id == prescription.patient_id,
        Appointment.doctor_id == current_doctor.id
    ).first()

    if not appointment:
        raise HTTPException(status_code=403, detail="No appointment found with this patient for the current doctor.")

    new_prescription = Prescription(
        appointment_id=appointment.id,
        doctor_id=current_doctor.id,
        patient_id=prescription.patient_id,
        issue_details=prescription.issue_details,
        medicines=prescription.medicines
    )
    db.add(new_prescription)
    db.commit()
    db.refresh(new_prescription)
    return new_prescription

@router.get("/prescriptions/", response_model=List[PrescriptionOut])
def get_prescriptions_for_patient(db: Session = Depends(get_db), current_user: User = Depends(get_current_patient)):
    return db.query(Prescription).filter_by(patient_id=current_user.id).all()

