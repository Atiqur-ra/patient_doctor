from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from cryptography.fernet import Fernet, InvalidToken as FernetInvalidToken
import os
from dotenv import load_dotenv
import json
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ENCRIPTION_KEY = os.getenv("ENCRIPTION_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY must be set in the environment variables")
if not ENCRIPTION_KEY:
    raise ValueError("FERNET_KEY must be set in the environment variables")


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
fernet = Fernet(ENCRIPTION_KEY.encode())

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": int(expire.timestamp())})


    json_data = json.dumps(to_encode).encode()
    encrypted_data = fernet.encrypt(json_data)
    return jwt.encode({"data": encrypted_data.decode()}, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        encrypted_data = payload.get("data")
        if not encrypted_data:
            raise JWTError("Missing encrypted data")

        decrypted_json = fernet.decrypt(encrypted_data.encode())
        return json.loads(decrypted_json)

    except (JWTError, FernetInvalidToken, json.JSONDecodeError):
        raise JWTError("Invalid or corrupted token")
    
