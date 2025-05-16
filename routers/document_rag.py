from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from models import User, Document, Appointment
from database import get_db
from external.document_upload import handle_document_upload
from auth import get_current_doctor
import os
from external.document_query import handle_document_query
from fastapi import Form
from better_profanity import profanity

profanity.load_censor_words()

router = APIRouter(prefix="/rag", tags=["DOCUMENT Query"])


@router.post("/upload-to-pinecone/")
def upload_patient_doc_to_pinecone(
    patient_id: int = Query(None),
    patient_name: str = Query(None),
    current_user: User = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):
    if not patient_id and not patient_name:
        raise HTTPException(status_code=400, detail="Provide either patient_id or patient_name")

 
    query = db.query(User)
    if patient_id:
        query = query.filter(User.id == patient_id)
    elif patient_name:
        query = query.filter(User.name == patient_name)

    patient = query.first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")


    document = (
        db.query(Document)
        .join(Appointment)
        .filter(Document.uploaded_by_id == patient.id)
        .order_by(Document.id.desc())
        .first()
    )

    if not document:
        raise HTTPException(status_code=404, detail="No document found for this patient")

    if not os.path.exists(document.path):
        raise HTTPException(status_code=404, detail="Document file not found on disk")

    with open(document.path, "rb") as uploaded_file:
        handle_document_upload(
            uploaded_file=uploaded_file,
            chat_name=str(patient.name),
            patient_id=patient.id,
            db=db
        )

    return {"message": "Document indexed into Pinecone successfully"}


@router.post("/query/")
def query_patient_document(
    patient_identifier: str = Form(...),
    question: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor)
):
    try:
        if profanity.contains_profanity(question):
            return {'message': "Please ask a valid query"}

        if patient_identifier.isdigit():
            patient_id = int(patient_identifier)
        else:
            patient = db.query(User).filter(User.name == patient_identifier).first()
            if not patient:
                raise HTTPException(status_code=404, detail="Patient not found")
            patient_id = patient.id


        user = db.query(User).filter(User.id == patient_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Patient not found")

        answer = handle_document_query(chat_name=str(user.name), question=question)

        return {"answer": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
