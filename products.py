from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from sqlalchemy.orm import Session
from database import get_db
from models import Product, Tag
import os
from uuid import uuid4
from typing import Optional, List
import json

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
    tags: str = Form("[]"),
    file: Optional[UploadFile] = None,
    db: Session = Depends(get_db)
):
    if not name or not description or not category:
        raise HTTPException(status_code=400, detail="All fields are required.")

    try:
        tags_list = json.loads(tags)
        if not isinstance(tags_list, list):
            raise ValueError
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid tags format. Must be a JSON list.")

    image_url = None
    if file:
        file_extension = file.filename.split(".")[-1].lower()
        if file_extension not in ["jpg", "jpeg", "png", "webp"]:
            raise HTTPException(status_code=400, detail="Invalid image format")

        unique_filename = f"{uuid4()}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        image_url = f"{BASE_URL}/uploads/{unique_filename}"

    # ✅ Create product first
    new_product = Product(
        name=name,
        price=price,
        stock=stock,
        description=description,
        category=category,
        image_url=image_url,
        tags=[]  # Initialize empty list for tags
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    # ✅ Associate tags **after** creating the product
    for tag_name in tags_list:
        tag = db.query(Tag).filter(Tag.name == tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
            db.commit()
            db.refresh(tag)
        new_product.tags.append(tag)  # Append to relationship

    db.commit()  # Final commit after all associations are done
    db.refresh(new_product)  # Refresh to get updated data

    return new_product
