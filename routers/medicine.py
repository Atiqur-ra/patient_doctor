from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.medicine_model import Medicine,PatientPurchase,PurchaseItem
from schemas import MedicineCreate, MedicineUpdate, MedicineOut
from auth import get_current_pharmacy_user
from typing import List
from fastapi import Query
from models.prescription_model import Prescription
from auth import get_current_patient
from models.user_model import User
from typing import Optional
from schemas import BillResponse
from schemas import BillCreate
from schemas import BillMedicineItem
from schemas import PurchaseRequest
from models.medicine_model import Billing
from models.medicine_model import BillingItem
from models.medicine_model import MedicineImage
from external.ocr import extract_text_from_image
import os
from fastapi import UploadFile, File
from typing import Dict, Any
from schemas import PurchaseRequest

router = APIRouter(prefix="/medicines", tags=["Medicines"])

@router.post("/", response_model=MedicineOut)
def create_medicine(medicine: MedicineCreate, db: Session = Depends(get_db), current_user = Depends(get_current_pharmacy_user)):
    db_medicine = Medicine(**medicine.dict())
    db.add(db_medicine)
    db.commit()
    db.refresh(db_medicine)
    return db_medicine

@router.get("/", response_model=List[MedicineOut])
def list_medicines(db: Session = Depends(get_db), current_user = Depends(get_current_pharmacy_user)):
    return db.query(Medicine).all()

@router.put("/{medicine_id}", response_model=MedicineOut)
def update_medicine(medicine_id: int, update: MedicineUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_pharmacy_user)):
    medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    medicine.quantity = update.quantity
    medicine.price = update.price
    db.commit()
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
    current_user: User = Depends(get_current_pharmacy_user),
    db: Session = Depends(get_db)
):
    query = db.query(Prescription).join(User, Prescription.patient_id == User.id)

    if patient_id:
        query = query.filter(Prescription.patient_id == patient_id)
    elif patient_name:
        query = query.filter(User.name.ilike(f"%{patient_name}%"))
    else:
        raise HTTPException(status_code=400, detail="Provide patient_id or patient_name")

    prescriptions = query.all()
    return prescriptions




@router.post("/create-bill", response_model=dict)
def create_bill(
    bill: BillCreate,
    current_user: User = Depends(get_current_pharmacy_user),
    db: Session = Depends(get_db)
):

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
        pharmacy_staff_id=current_user['id'],
        total_price=total_price,
        items=billing_items
    )

    db.add(billing)
    db.commit()
  

    return {
        "message": "Billing completed",
        "patient_name": patient.name,
        "total_price": total_price,
        "billed_by": current_user['name']
    }

@router.get("/pharmacy/dispense")
def get_bill_by_patient(
    patient_id: Optional[int] = Query(None),
    patient_name: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_pharmacy_user)
):

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

@router.get("/search/medicine/patient")
def medicine_search_patient(
    db: Session = Depends(get_db),
    medicine_name: Optional[str] = None,
    current_user: User = Depends(get_current_patient)
):
   
    if not medicine_name:
        medicines = db.query(Medicine).all()
    else:
        medicines = db.query(Medicine).filter(Medicine.name.ilike(f"%{medicine_name}%")).all()
    if not medicines:
        raise HTTPException(status_code=404, detail="No medicines found")
    
    return medicines


@router.post("/patient/buy_medicine", response_model=Dict[str, Any])
def buy_medicines(
    request: PurchaseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
    
):
    if not request.medicines or request.patient_id is None:
        raise HTTPException(status_code=400, detail="Medicines and patient ID are required")

    total_cost = 0
    purchase_items = []

    for item in request.medicines:
        med = db.query(Medicine).filter(Medicine.id == item.medicine_id).first()
        if not med:
            raise HTTPException(status_code=404, detail=f"Medicine ID {item.medicine_id} not found")
        if med.quantity < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {med.name}")

    
        med.quantity -= item.quantity
        cost = med.price * item.quantity
        total_cost += cost

        purchase_items.append(PurchaseItem(
            medicine_id=med.id,
            quantity=item.quantity,
            price=cost
        ))

    purchase = PatientPurchase(
        patient_id=current_user['id'],
        total_amount=total_cost,
        items=purchase_items
    )

    db.add(purchase)
    db.commit()

    return {"message": "Medicines purchased successfully", "total_amount": total_cost}


@router.post("/upload-medicine-image")
def upload_medicine_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_pharmacy_user)
):
    contents = file.file.read()
    text = extract_text_from_image(contents)


    save_path = f"uploads/medicine_images/{file.filename}"
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "wb") as f:
        f.write(contents)


    image_record = MedicineImage(
        filename=file.filename,
        extracted_text=text,
        uploaded_by=current_user['id']
    )
    db.add(image_record)
    db.commit()


    return {
        "message": "Image uploaded and text extracted successfully",
        "extracted_text": text
    }