from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional
from datetime import datetime

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

class TagResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        orm_mode = True

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    stock: int
    category: str
    image_url: Optional[str] = None  # ✅ Made image optional
    tags: List[str] = []

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    stock: int
    category: str
    image_url: Optional[str] = None
    tags: List[TagResponse] = []

    class Config:
        orm_mode = True

    @validator('tags', pre=True)
    def extract_tag_names(cls, tags):
        return [{'id': tag.id, 'name': tag.name} if hasattr(tag, 'name') else tag for tag in tags]

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_price: float
    quantity: int

    class Config:
        orm_mode = True

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
