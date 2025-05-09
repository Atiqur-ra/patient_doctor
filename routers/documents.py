import os
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Document, Appointment, User
from utils.security import get_current_user
from fastapi.responses import FileResponse, StreamingResponse
from schemas import DocumentPreviewOut

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("/patient-documents/preview")
def preview_patient_document(
    patient_id: int = Query(..., description="Patient ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can access this")

    # Get latest appointment between this doctor and patient
    document = (
        db.query(Document)
        .join(Document.appointment)
        .filter(
            Document.uploaded_by_id == patient_id,
            Document.appointment.has(doctor_id=current_user.id)
        )
        .order_by(Document.id.desc())
        .first()
    )

    if not document:
        raise HTTPException(status_code=404, detail="No document found for this patient")

    if not os.path.exists(document.path):
        raise HTTPException(status_code=404, detail="File missing on server")

    return StreamingResponse(
        open(document.path, "rb"),
        media_type=document.content_type,
        headers={"Content-Disposition": f'inline; filename="{document.filename}"'}
    )



@router.get("/view/{document_id}")
def view_document(document_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Only the doctor who has appointment with this patient can see it
    if current_user.role == "doctor":
        if document.appointment.doctor_id != current_user.id:
            raise HTTPException(status_code=403, detail="Unauthorized")
    else:
        raise HTTPException(status_code=403, detail="Only doctors can view documents")

    return FileResponse(
        path=document.path,
        media_type=document.content_type,
        filename=document.filename
    )