from app import models, security
from app.database import SessionLocal

EMAIL = "admin@blooddonorfinder.com"
PASSWORD = "Admin@12345"

db = SessionLocal()
if db.query(models.User).filter(models.User.email == EMAIL).first():
    print("Admin already exists")
else:
    db.add(models.User(name="Admin", email=EMAIL,
                       password_hash=security.hash_password(PASSWORD),
                       role="admin", is_approved=True))
    db.commit()
    print("Admin created")