from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional
from datetime import datetime

# ✅ User Schemas
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

# ✅ Authentication Schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# ✅ Tag Schemas
class TagResponse(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

# ✅ Product Schemas
class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    stock: int
    category: str
    image_url: Optional[str] = None 
    tags: List[str] = []

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    stock: int
    category: str
    image_url: Optional[str] = None
    tags: List[str]  # ✅ Changed to return tag names directly

    class Config:
        orm_mode = True

    @validator('tags', pre=True)
    def extract_tag_names(cls, tags):
        if isinstance(tags, list) and len(tags) > 0:
            if isinstance(tags[0], dict):  
                return [tag["name"] for tag in tags]  # Handles JSON-style objects
            elif hasattr(tags[0], "name"):  
                return [tag.name for tag in tags]  # Handles SQLAlchemy ORM objects
        return []

# ✅ Cart Schemas
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

# ✅ Order Schemas
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
