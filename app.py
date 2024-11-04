import os
from datetime import timedelta, datetime
import jwt
from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware
from database import SessionLocal, engine
from models import Base, User, FundFamily, Watchlist
from schemas import LoginRequest, FundFamilyRequest, WatchlistItem
import requests
from passlib.context import CryptContext

# Initialize FastAPI app
app = FastAPI()

# Environment variables and configurations
SECRET_KEY = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# CORS middleware settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# JWT Token creation and verification
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "sub": data.get("user_id")})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")


# Dependency to get current user from token
def verify_token_dependency(authorization: str = Header(...)):
    try:
        token = authorization.split(" ")[1]
        return verify_token(token)
    except IndexError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token format")


# Database initialization on startup
@app.on_event("startup")
def startup_populate_db():
    db = SessionLocal()
    fund_families = [
        # List of fund families
        "SBI Mutual Fund", "HDFC Mutual Fund", "ICICI Prudential Mutual Fund",
        "Axis Mutual Fund", "Nippon India Mutual Fund", "UTI Mutual Fund",
        "Aditya Birla Sun Life Mutual Fund", "Kotak Mutual Fund",
        "Tata Mutual Fund", "Franklin Templeton Mutual Fund",
        "Mirae Asset Mutual Fund", "DSP Mutual Fund", "Invesco Mutual Fund",
        "Edelweiss Mutual Fund", "Motilal Oswal Mutual Fund", "IDFC Mutual Fund",
        "L&T Mutual Fund", "Canara Robeco Mutual Fund", "Quantum Mutual Fund",
        "Mahindra Manulife Mutual Fund", "PPFAS Mutual Fund", "HSBC Mutual Fund",
        "Baroda BNP Paribas Mutual Fund", "Principal Mutual Fund",
        "Sundaram Mutual Fund"
    ]

    for family in fund_families:
        if not db.query(FundFamily).filter(FundFamily.name == family).first():
            db.add(FundFamily(name=family))

    db.commit()
    db.close()


# Create database tables
Base.metadata.create_all(bind=engine)


# Define routes
@app.get("/", response_class=HTMLResponse)
async def read_index():
    return FileResponse("static/login.html")


@app.get("/register", response_class=HTMLResponse)
async def read_register():
    return FileResponse("static/register.html")


@app.post("/login")
async def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_request.email).first()
    if not user or not pwd_context.verify(login_request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"user_id": user.id})
    return {"message": "Login successful", "access_token": access_token}


@app.post("/register")
async def register(register: LoginRequest, db: Session = Depends(get_db)):
    if not register.email or not register.password:
        raise HTTPException(status_code=400, detail="All fields are required")

    if db.query(User).filter(User.email == register.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed_password = pwd_context.hash(register.password)
    new_user = User(email=register.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully", "email": new_user.email}


@app.post("/fetch_funds")
async def fetch_funds(fund_family: FundFamilyRequest, user_id: str = Depends(verify_token_dependency)):
    api_key = os.getenv("RAPIDAPI_KEY")
    url = f"https://latest-mutual-fund-nav.p.rapidapi.com/latest?Mutual_Fund_Family={fund_family.family}"

    response = requests.get(url, headers={"x-rapidapi-key": api_key})

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching funds")

    return response.json()


@app.get("/fund_family", response_model=list)
async def get_fund_family(user_id: str = Depends(verify_token_dependency), db: Session = Depends(get_db)):
    return [{"id": family.id, "name": family.name} for family in db.query(FundFamily).all()]


@app.get("/dashboard", response_class=HTMLResponse)
async def read_dashboard():
    return FileResponse("static/dashboard.html")


@app.post("/addtowatchlist")
async def add_to_watchlist(watchlist_item: WatchlistItem, user_id: str = Depends(verify_token_dependency),
                           db: Session = Depends(get_db)):
    fund_family = db.query(FundFamily).filter(FundFamily.name == watchlist_item.fund_family_id).first()
    if not fund_family:
        raise HTTPException(status_code=404, detail="Fund family not found")

    new_watchlist_item = Watchlist(user_id=user_id, fund_family_id=watchlist_item.scheme_code)
    db.add(new_watchlist_item)
    db.commit()
    db.refresh(new_watchlist_item)

    return {"message": "Item added to watchlist", "item_id": new_watchlist_item.id}


@app.get("/watchlist", response_class=HTMLResponse)
async def read_watchlist():
    return FileResponse("static/watchlist.html")


@app.post("/fetch_funds_from_watchlist")
async def fetch_funds_from_watchlist(user_id: str = Depends(verify_token_dependency), db: Session = Depends(get_db)):
    watchlist_items = db.query(Watchlist).filter(Watchlist.user_id == user_id).all()
    if not watchlist_items:
        raise HTTPException(status_code=404, detail="No funds in the portfolio")

    funds_data = []
    for item in watchlist_items:
        api_key = os.getenv("RAPIDAPI_KEY")
        url = f"https://latest-mutual-fund-nav.p.rapidapi.com/latest?Scheme_Type=Open&Scheme_Code={item.fund_family_id}"

        response = requests.get(url, headers={"x-rapidapi-key": api_key})
        if response.status_code != 200:
            continue  # Skip this fund if there is an error in fetching data

        fund_data = response.json()
        funds_data.append({"scheme_code": item.fund_family_id, "fund_data": fund_data})

    if not funds_data:
        raise HTTPException(status_code=404, detail="No funds in the portfolio")

    return funds_data