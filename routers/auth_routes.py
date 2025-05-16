from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from utils.security import create_access_token
from database import get_db
from models.user_model import User
from datetime import timedelta
from schemas import MagicLinkRequest, MagicLinkPayload
from utils.security import decode_access_token
from fastapi import Query

router = APIRouter(prefix="/auth", tags=["Auth"])



@router.post("/magic-link/send")
def send_magic_link(data: MagicLinkRequest, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token_data = {
        "sub": user.email,
        "id": user.id,
        "role": user.role,
        "name": user.name
    }

    token = create_access_token(data=token_data, expires_delta=timedelta(minutes=10))
    magic_link = f"{request.base_url}auth/magic-link/verify?token={token}"

    return {"link": magic_link}

@router.get("/magic-link/verify")
def verify_magic_link(link: str = Query(...)):
    try:
        token = link.split("token=")[-1] 


        payload = decode_access_token(token)
        return {"message": f"{payload['name']} successfully logged in"}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")