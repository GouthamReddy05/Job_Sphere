from datetime import datetime, timedelta
from jose import jwt
from fastapi import Request, HTTPException
import hashlib
SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def normalize_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not Logged In")

    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    return payload["user_id"]