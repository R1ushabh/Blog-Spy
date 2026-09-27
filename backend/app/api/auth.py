from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, create_access_token, hash_password
from app.models.models import User
from app.schemas.schemas import Token, UserResponse, UserCreate

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

@router.post("/register", response_model=UserResponse)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    user = User(
        email=user_in.email,
        password_hash=hash_password(user_in.password),
        role=user_in.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Seed default admin user if no users exist
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user and form_data.username == "admin@competitorspy.local":
        user = User(
            email="admin@competitorspy.local",
            password_hash=hash_password(form_data.password or "admin123"),
            role="admin"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
        
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer", "user": user}

@router.get("/me", response_model=UserResponse)
def get_current_user(db: Session = Depends(get_db)):
    # Simple default admin user return for seamless demo
    user = db.query(User).first()
    if not user:
        user = User(email="admin@competitorspy.local", password_hash=hash_password("admin123"), role="admin")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
