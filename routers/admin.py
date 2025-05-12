from fastapi import APIRouter, Depends, HTTPException
from schemas import UserUpdate
from sqlalchemy.orm import Session
from database import get_db
from auth import get_admin_user
from models import User, Medicine, Appointment, Prescription, Review

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/users")
def list_all_users(db: Session = Depends(get_db), admin_user: User = Depends(get_admin_user)):
    return db.query(User).all()

@router.get("/appointments")
def list_all_appointments(db: Session = Depends(get_db), admin_user: User = Depends(get_admin_user)):
    return db.query(Appointment).all()

@router.get("/medicines")
def list_all_medicines(db: Session = Depends(get_db), admin_user: User = Depends(get_admin_user)):
    return db.query(Medicine).all()

@router.get("/prescriptions")
def list_all_prescriptions(db: Session = Depends(get_db), admin_user: User = Depends(get_admin_user)):
    return db.query(Prescription).all()

@router.get("/reviews")
def list_all_reviews(db: Session = Depends(get_db), admin_user: User = Depends(get_admin_user)):
    return db.query(Review).all()

@router.put("/users/{user_id}")
def update_user_by_admin(
    user_id: int,
    update_data: UserUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for attr, value in update_data.dict(exclude_unset=True).items():
        setattr(user, attr, value)

    db.commit()
    db.refresh(user)
    return {"message": "User updated successfully", "user": user}


@router.delete("/users/{user_id}")
def delete_user_by_admin(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": f"User with ID {user_id} has been deleted"}
