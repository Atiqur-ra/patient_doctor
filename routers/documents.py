import os
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models.user_model import User
from models.documents_model import Document
from utils.security import get_current_user
from fastapi.responses import FileResponse, StreamingResponse
from auth import get_current_patient
from typing import List
from schemas import DocumentOut



UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("/patient-documents/preview-doctor")
def preview_patient_documents(
    patient_id: int = Query(..., description="Patient ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can access this")

    documents = (
        db.query(Document)
        .join(Document.appointment)
        .filter(
            Document.uploaded_by_id == patient_id,
            Document.appointment.has(doctor_id=current_user.id)
        )
        .order_by(Document.id.desc())
        .all()
    )

    if not documents:
        raise HTTPException(status_code=404, detail="No documents found for this patient")


    return [
        DocumentOut(
            id=doc.id,
            filename=doc.filename,
            content_type=doc.content_type,
            document_id=f"{doc.id}"
        )
        for doc in documents
    ]

@router.get("/view_doctor/{doc_id}")
def download_document(doc_id: int, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can access this")
    document = db.query(Document).filter(Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if not os.path.exists(document.path):
        raise HTTPException(status_code=404, detail="File missing on server")

    return StreamingResponse(
        open(document.path, "rb"),
        media_type=document.content_type,
        headers={"Content-Disposition": f'inline; filename="{document.filename}"'}
    )

@router.get("/dowload_doctor/{document_id}")
def view_document(document_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can access this")
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.appointment.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    

    return FileResponse(
        path=document.path,
        media_type=document.content_type,
        filename=document.filename
    )

@router.get("/patient-documents/preview-patient", response_model=List[DocumentOut])
def preview_patient_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Only patient can access this")

    documents = (
        db.query(Document)
        .join(Document.appointment)
        .filter(
            Document.uploaded_by_id == current_user.id,
        )
        .order_by(Document.id.desc())
        .all()
    )

    if not documents:
        raise HTTPException(status_code=404, detail="No documents found for this patient")

    # Return document metadata including preview/download URL
    return [
        DocumentOut(
            id=doc.id,
            filename=doc.filename,
            content_type=doc.content_type,
            document_id=f"{doc.id}"
        )
        for doc in documents
    ]


@router.get("/patient-documents/view/{doc_id}")
def download_document(doc_id: int, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Only patient can access this")
    document = db.query(Document).filter(Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if not os.path.exists(document.path):
        raise HTTPException(status_code=404, detail="File missing on server")

    return StreamingResponse(
        open(document.path, "rb"),
        media_type=document.content_type,
        headers={"Content-Disposition": f'inline; filename="{document.filename}"'}
    )


@router.get("/patient-documents/download/{document_id}")
def view_document(document_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Only patient can access this")
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")


    if current_user.role == "patient":
        if document.appointment.patient_id != current_user.id:
            raise HTTPException(status_code=403, detail="Unauthorized")
    else:
        raise HTTPException(status_code=403, detail="Only patient can view documents")

    return FileResponse(
        path=document.path,
        media_type=document.content_type,
        filename=document.filename
    )
