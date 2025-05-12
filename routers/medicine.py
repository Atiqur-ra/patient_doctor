from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Medicine
from schemas import MedicineCreate, MedicineUpdate, MedicineOut
from auth import get_current_pharmacy_user
from typing import List
from fastapi import Query
from models import Prescription
from auth import get_current_user
from models import User
from typing import Optional
from fastapi import Query
from schemas import BillResponse
from schemas import BillCreate
from schemas import BillMedicineItem
from models import Billing, BillingItem, MedicineImage
from utils.ocr import extract_text_from_image
import os
from fastapi import UploadFile, File


router = APIRouter(prefix="/medicines", tags=["Medicines"])

@router.post("/", response_model=MedicineOut)
def create_medicine(medicine: MedicineCreate, db: Session = Depends(get_db), current_user = Depends(get_current_pharmacy_user)):
    db_medicine = Medicine(**medicine.dict())
    db.add(db_medicine)
    db.commit()
    db.refresh(db_medicine)
    return db_medicine

@router.get("/", response_model=List[MedicineOut])
def list_medicines(db: Session = Depends(get_db)):
    return db.query(Medicine).all()

@router.put("/{medicine_id}", response_model=MedicineOut)
def update_medicine(medicine_id: int, update: MedicineUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_pharmacy_user)):
    medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    medicine.quantity = update.quantity
    medicine.price = update.price
    db.commit()
    db.refresh(medicine)
    return medicine

@router.delete("/{medicine_id}")
def delete_medicine(medicine_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_pharmacy_user)):
    medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    db.delete(medicine)
    db.commit()
    return {"message": "Medicine deleted"}


@router.get("/pharmacy/prescriptions")
def get_prescriptions_for_patient(
    patient_id: Optional[int] = Query(None),
    patient_name: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "pharmacy":
        raise HTTPException(status_code=403, detail="Only pharmacy staff can access this")

    query = db.query(Prescription).join(User, Prescription.patient_id == User.id)

    if patient_id:
        query = query.filter(Prescription.patient_id == patient_id)
    elif patient_name:
        query = query.filter(User.name.ilike(f"%{patient_name}%"))
    else:
        raise HTTPException(status_code=400, detail="Provide patient_id or patient_name")

    prescriptions = query.all()
    return prescriptions


# routers/medicine.py

@router.post("/create-bill", response_model=dict)
def create_bill(
    bill: BillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "pharmacy":
        raise HTTPException(status_code=403, detail="Only pharmacy staff can create bills")

    patient = db.query(User).filter(User.id == bill.patient_id, User.role == "patient").first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    total_price = 0
    billing_items = []

    for item in bill.items:
        medicine = db.query(Medicine).filter(Medicine.id == item.medicine_id).first()
        if not medicine:
            raise HTTPException(status_code=404, detail=f"Medicine ID {item.medicine_id} not found")
        if medicine.quantity < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for {medicine.name}")
        
        medicine.quantity -= item.quantity
        item_price = medicine.price * item.quantity
        total_price += item_price

        billing_items.append(BillingItem(
            medicine_id=medicine.id,
            quantity=item.quantity,
            price_per_unit=medicine.price
        ))

    billing = Billing(
        patient_id=bill.patient_id,
        pharmacy_staff_id=current_user.id,
        total_price=total_price,
        items=billing_items
    )

    db.add(billing)
    db.commit()
    db.refresh(billing)

    return {
        "message": "Billing completed",
        "patient_name": patient.name,
        "total_price": total_price,
        "billed_by": current_user.name
    }

@router.get("/pharmacy/dispense", response_model=BillResponse)
def get_bill_by_patient(
    patient_id: Optional[int] = Query(None),
    patient_name: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "pharmacy":
        raise HTTPException(status_code=403, detail="Only pharmacy staff can access this")

    if not patient_id and not patient_name:
        raise HTTPException(status_code=400, detail="Provide patient_id or patient_name")

    query = db.query(User).filter(User.role == "patient")
    if patient_id:
        query = query.filter(User.id == patient_id)
    elif patient_name:
        query = query.filter(User.name.ilike(f"%{patient_name}%"))

    patient = query.first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    billing = db.query(Billing)\
                .filter(Billing.patient_id == patient.id)\
                .order_by(Billing.created_at.desc())\
                .first()

    if not billing:
        raise HTTPException(status_code=404, detail="No billing found")

    medicines = [
        BillMedicineItem(medicine_name=item.medicine.name, quantity=item.quantity)
        for item in billing.items
    ]

    return BillResponse(
        patient_name=patient.name,
        billed_by=billing.pharmacy_staff.name,
        medicines=medicines,
        total_amount=billing.total_price
    )

@router.post("/upload-medicine-image")
def upload_medicine_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "pharmacy":
        raise HTTPException(status_code=403, detail="Only pharmacy staff can upload medicine images")

    contents = file.file.read()
    text = extract_text_from_image(contents)

    # Optional: save file to disk
    save_path = f"uploads/medicine_images/{file.filename}"
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "wb") as f:
        f.write(contents)

    # Save to database
    image_record = MedicineImage(
        filename=file.filename,
        extracted_text=text,
        uploaded_by=current_user.id
    )
    db.add(image_record)
    db.commit()
    db.refresh(image_record)

    return {
        "message": "Image uploaded and text extracted successfully",
        "extracted_text": text
    }