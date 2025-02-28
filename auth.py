from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jwt import encode

from database import get_db
from models import User, Product, Tag
from schemas import UserCreate, UserResponse, LoginRequest, Token, ProductCreate, ProductResponse
from config import SECRET_KEY, ALGORITHM
from dependencies import get_current_user, get_current_admin

router = APIRouter(tags=["Authentication"])

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token expiration time (30 minutes)
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ------------------- SIGNUP -------------------
@router.post("/signup", response_model=UserResponse)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_password = pwd_context.hash(user_data.password)

    new_user = User(
        email=user_data.email,
        password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone_number=user_data.phone_number
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

# ------------------- LOGIN -------------------
@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user or not pwd_context.verify(login_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}

# ------------------- ADMIN ACCOUNT CREATION -------------------
@router.post("/create-admin", response_model=UserResponse)
def create_admin(user_data: UserCreate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_password = pwd_context.hash(user_data.password)

    new_admin = User(
        email=user_data.email,
        password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone_number=user_data.phone_number,
        is_admin=True
    )

    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    return new_admin

# ------------------- DELETE ACCOUNT -------------------
@router.delete("/delete-account")
def delete_account(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == current_user.email).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins cannot delete themselves")

    db.delete(user)
    db.commit()
    
    return {"message": "Account deleted successfully"}

# ------------------- PROTECTED ROUTE -------------------
@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# ------------------- ADD PRODUCT (ADMIN ONLY) -------------------
@router.post("/admin/add-product", response_model=ProductResponse)
def add_product(product_data: ProductCreate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    # Create product instance
    new_product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        stock=product_data.stock,
        category=product_data.category
    )

    # Process tags
    tag_objects = []
    for tag_name in product_data.tags:
        tag = db.query(Tag).filter(Tag.name == tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
        tag_objects.append(tag)

    new_product.tags = tag_objects

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product
