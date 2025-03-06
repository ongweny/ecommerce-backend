from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models import Product, Tag
from schemas import ProductCreate, ProductResponse
from dependencies import get_current_admin
from typing import List


router = APIRouter()

# ✅ Add a Product
@router.post("/add-product", response_model=ProductResponse)
def add_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    # Check for duplicate product name
    existing_product = db.query(Product).filter(Product.name == product_data.name).first()
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this name already exists"
        )

    # Create new product
    new_product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        stock=product_data.stock,
        category=product_data.category,
    )

    # Handle tags (ensure they exist or create new ones)
    tags = []
    for tag_name in product_data.tags:
        tag = db.query(Tag).filter(Tag.name == tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
            db.commit()
            db.refresh(tag)
        tags.append(tag)
    new_product.tags = tags

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product

# ✅ Get All Products
@router.get("/products/", response_model=List[ProductResponse])
def get_products(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    products = db.query(Product).all()
    return products

# ✅ Delete Product
@router.delete("/delete-product/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db), current_admin: dict = Depends(get_current_admin)):
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    db.delete(product)
    db.commit()
    
    return {"message": "Product deleted successfully"}
