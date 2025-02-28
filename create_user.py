from database import SessionLocal
from models import User
from passlib.context import CryptContext

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create a database session
db = SessionLocal()

# Define the user details
new_user = User(
    email="user@example.com",
    password=pwd_context.hash("secret"),  # Use "password" if your model uses that field
    first_name="John",
    last_name="Doe",
    phone_number="123456789"
)

# Add and commit the new user
db.add(new_user)
db.commit()

# Close the database session
db.close()

print("User created successfully!")
