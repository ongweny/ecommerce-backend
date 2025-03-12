from pydantic import BaseModel, EmailStr, validator
from typing import List
from datetime import datetime

# ------------------- USER SCHEMAS -------------------
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone_number: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    phone_number: str
    is_admin: bool

    class Config:
        orm_mode = True

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# ------------------- TAG SCHEMA -------------------
class TagResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        orm_mode = True

# ------------------- PRODUCT SCHEMAS -------------------
class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    stock: int
    category: str
    tags: List[str] = []

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    stock: int
    category: str
    tags: List[TagResponse] = []

    class Config:
        orm_mode = True

    @validator('tags', pre=True)
    def extract_tag_names(cls, tags):
        return [{'id': tag.id, 'name': tag.name} if hasattr(tag, 'name') else tag for tag in tags]

# ------------------- CART SCHEMAS -------------------
class CartItemCreate(BaseModel):
    product_id: int
    quantity: int

class CartItemResponse(BaseModel):
    id: int  # ✅ Kept `cart.id`
    product_id: int  # ✅ Changed back to product_id instead of full ProductResponse
    product_name: str  # ✅ Included for easier frontend use
    product_price: float  # ✅ Included for easier frontend use
    quantity: int

    class Config:
        orm_mode = True

# ------------------- ORDER SCHEMAS -------------------
class OrderCreate(BaseModel):
    product_id: int
    quantity: int

class OrderResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    total_price: float
    created_at: datetime

    class Config:
        orm_mode = True
