from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from sqlalchemy.orm import Session
from database import get_db
from models import Product, Tag
import os
from uuid import uuid4
from typing import Optional, List
import json
# from fastapi.staticfiles import StaticFiles

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

BASE_URL = "http://localhost:8080"

# ----------------- Image Upload Endpoint -----------------
@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ["jpg", "jpeg", "png", "webp"]:
        raise HTTPException(status_code=400, detail="Invalid image format")

    unique_filename = f"{uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    return {"image_url": f"{BASE_URL}/uploads/{unique_filename}"}

# ----------------- Add Product Endpoint -----------------
@router.post("/products")
async def add_product(
    name: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    tags: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    print(f"📩 Received Form Data: name={name}, price={price}, stock={stock}, description={description}, category={category}")
    print(f"Tags: {tags}, Image: {image.filename if image else 'No Image'}")

    if not name or not description or not category:
        raise HTTPException(status_code=400, detail="All fields are required.")

    # ✅ Handle tags properly
    tags_list = []
    if tags:
        try:
            tags_list = json.loads(tags)  # Convert JSON string to list
            if not isinstance(tags_list, list):
                raise ValueError
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid tags format. Must be a JSON list.")

    # ✅ Handle image upload properly
    image_url = None
    if image:
        file_extension = image.filename.split(".")[-1].lower()
        if file_extension not in ["jpg", "jpeg", "png", "webp"]:
            raise HTTPException(status_code=400, detail="Invalid image format")

        unique_filename = f"{uuid4()}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        with open(file_path, "wb") as buffer:
            buffer.write(await image.read())

        image_url = f"{BASE_URL}/uploads/{unique_filename}"

    # ✅ Save to DB
    new_product = Product(
        name=name,
        price=price,
        stock=stock,
        description=description,
        category=category,
        image_url=image_url
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {"message": "Product added successfully", "product": new_product}

# ----------------- Get All Products Endpoint -----------------
@router.get("/products")
async def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products

