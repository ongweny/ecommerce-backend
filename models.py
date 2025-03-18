from sqlalchemy import Column, Integer, String, ForeignKey, Float, Table, Boolean, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

# ✅ Association table for product tags (many-to-many relationship)
product_tags = Table(
    "product_tags",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone_number = Column(String, unique=True, nullable=False)
    is_admin = Column(Boolean, default=False)

    # ✅ Cascade delete behavior added
    cart_items = relationship("Cart", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    saved_items = relationship("SavedItem", back_populates="user", cascade="all, delete-orphan")  # ✅ Added saved items

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    category = Column(String, nullable=False)
    image_url = Column(String, nullable=True) 

    # ✅ Many-to-Many Relationship with Tags
    tags = relationship("Tag", secondary=product_tags, back_populates="products")

    # ✅ One-to-Many Relationship with Cart, Orders, and Saved Items
    cart_items = relationship("Cart", back_populates="product", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="product", cascade="all, delete-orphan")
    saved_items = relationship("SavedItem", back_populates="product", cascade="all, delete-orphan")  # ✅ Added saved items

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    products = relationship("Product", secondary=product_tags, back_populates="tags")

class Cart(Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)

    # ✅ Proper relationships
    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # ✅ Proper relationships
    user = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders")

class SavedItem(Base):
    __tablename__ = "saved_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)

    # ✅ Relationship with User and Product
    user = relationship("User", back_populates="saved_items")
    product = relationship("Product", back_populates="saved_items")
