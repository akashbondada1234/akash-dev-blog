import os
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import get_db
from models import User

SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-in-production")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@akash.dev").lower()
if os.getenv("ENVIRONMENT", "development").lower() == "production" and SECRET_KEY == "change-this-secret-in-production":
    raise RuntimeError("Set a strong SECRET_KEY before running in production")
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)

def hash_password(value): return pwd_context.hash(value)
def verify_password(plain, hashed): return pwd_context.verify(plain, hashed)
def create_token(user_id): return jwt.encode({"sub": str(user_id), "exp": datetime.now(timezone.utc) + timedelta(hours=24)}, SECRET_KEY, algorithm=ALGORITHM)

def current_user(request: Request, token=Depends(oauth2_scheme), db: Session = Depends(get_db)):
    token = token or request.cookies.get("access_token")
    if not token: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    try: user_id = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]).get("sub")
    except JWTError: raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.get(User, int(user_id))
    if not user: raise HTTPException(status_code=401, detail="User not found")
    return user

def admin_user(user=Depends(current_user)):
    if user.email.lower() != ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Administrator access required")
    return user
