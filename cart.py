from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Cart, Product
from schemas import CartItemCreate, CartItemResponse
from dependencies import get_current_user

router = APIRouter()

# ---------------- ADD TO CART ----------------
@router.post("/add", response_model=CartItemResponse)
def add_to_cart(cart_item: CartItemCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Validate product existence
    product = db.query(Product).filter(Product.id == cart_item.product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    # Validate stock availability
    if cart_item.quantity <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity must be at least 1")
    if cart_item.quantity > product.stock:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough stock available")

    # Check if item is already in the cart
    existing_cart_item = db.query(Cart).filter(Cart.user_id == current_user.id, Cart.product_id == cart_item.product_id).first()
    
    if existing_cart_item:
        # Update quantity only if within stock limit
        if existing_cart_item.quantity + cart_item.quantity > product.stock:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough stock for this update")
        existing_cart_item.quantity += cart_item.quantity
    else:
        # Create new cart item
        new_cart_item = Cart(user_id=current_user.id, product_id=cart_item.product_id, quantity=cart_item.quantity)
        db.add(new_cart_item)

    db.commit()
    db.refresh(existing_cart_item if existing_cart_item else new_cart_item)
    return existing_cart_item if existing_cart_item else new_cart_item

# ---------------- VIEW CART ----------------
@router.get("/", response_model=list[CartItemResponse])
def view_cart(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    cart_items = (
        db.query(Cart, Product.name, Product.price)
        .join(Product, Cart.product_id == Product.id)
        .filter(Cart.user_id == current_user.id)
        .all()
    )

    return [
        CartItemResponse(
            id=item.Cart.id,
            product_id=item.Cart.product_id,
            quantity=item.Cart.quantity,
            product_name=item.name,
            product_price=item.price
        )
        for item in cart_items
    ]

# ---------------- REMOVE FROM CART ----------------
@router.delete("/remove/{product_id}")
def remove_from_cart(product_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    cart_item = db.query(Cart).filter(Cart.user_id == current_user.id, Cart.product_id == product_id).first()

    if not cart_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not in cart")

    db.delete(cart_item)
    db.commit()
    
    return {"message": "Item removed from cart successfully"}
