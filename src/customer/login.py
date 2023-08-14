from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
import jwt
import re
from src.models.base import get_db
from src.models.customer import Customer, LoginCredential
from sqlalchemy.orm import Session
import os
from cryptography.fernet import Fernet

# get db session
db = get_db()

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable not set")

ALGORITHM = "RS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

login_router = APIRouter(
    prefix="/customer",
    tags=["customer"],
    responses={401: {"description": "Unauthorized"}},
)

class User(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: PhoneNumber

# Dependency to get the current user from the JWT token
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        public_key = os.environ.get("JWT_PUBLIC_KEY")
        if not public_key:
            raise ValueError("JWT_PUBLIC_KEY environment variable not set")

        payload = jwt.decode(token, public_key, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(Customer).filter(Customer.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

# Hashing and verifying passwords
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Create a new JWT token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    private_key = os.environ.get("JWT_PRIVATE_KEY")
    if not private_key:
        raise ValueError("JWT_PRIVATE_KEY environment variable not set")

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, private_key, algorithm=ALGORITHM)
    return encoded_jwt

# Login route
@login_router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(Customer).filter(Customer.email == form_data.username).first()
    if user:
        login_credential = db.query(LoginCredential).filter(LoginCredential.customer_id == user.customer_id).first()
        password_hash = login_credential.password if login_credential else None

        if password_hash and verify_password(form_data.password, password_hash):
            access_token = create_access_token(
                data={"sub": form_data.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            )
            return {"access_token": access_token, "token_type": "bearer"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

@login_router.post("/signup/")
def signup(customer: User, password: str, db: Session = Depends(get_db)):
    existing_customer = db.query(Customer).filter(Customer.email == customer.email).first()
    if existing_customer:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(password)

    new_customer = Customer(**customer.model_dump())
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    new_login_credential = LoginCredential(
        username=customer.email,
        password=hashed_password,
        customer_id=new_customer.customer_id,
        registration_date=datetime.now()
    )

    db.add(new_login_credential)
    db.commit()
    db.refresh(new_login_credential)

    return new_login_credential
