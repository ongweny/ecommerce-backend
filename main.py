from fastapi import FastAPI, Request
import logging
from auth import router as auth_router
from admin import router as admin_router
from cart import router as cart_router
from products import router as products_router
from database import engine
from models import Base, User
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
# ✅ Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Ensure database tables are created
Base.metadata.create_all(bind=engine)

# ✅ Function to create a default admin (runs only once)
def create_default_admin():
    with Session(bind=engine) as db:
        existing_admin = db.query(User).filter(User.email == "admin@example.com").first()
        if not existing_admin:
            default_admin = User(
                email="admin@example.com",
                password=pwd_context.hash("AdminPass123"),
                first_name="Admin",
                last_name="User",
                phone_number="1234567890",
                is_admin=True
            )
            db.add(default_admin)
            db.commit()
            print("✅ Default admin created: admin@example.com / AdminPass123")

# ✅ Call this function on startup
create_default_admin()

# ✅ Include all routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(cart_router, prefix="/cart", tags=["Cart"])
app.include_router(products_router, tags=["Products"]) 

@app.get("/")
def home():
    return {"message": "Welcome to the e-commerce backend!"}

# ✅ Logging Middleware for Debugging
logging.basicConfig(level=logging.INFO)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logging.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    return response
 
UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

