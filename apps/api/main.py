import os, json, uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Any
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from jose import jwt, JWTError
from passlib.context import CryptContext

SECRET = os.getenv("JWT_SECRET", "dev-only-change-me-before-deployment")
ALGORITHM = "HS256"
DB_URL = os.getenv("DATABASE_URL", "sqlite:///./rythu_mitra.db")
connect_args = {"check_same_thread": False} if DB_URL.startswith("sqlite") else {}
engine = create_engine(DB_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2 = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Record(Base):
    __tablename__ = "records"
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    module = Column(String(80), index=True, nullable=False)
    title = Column(String(240), nullable=False)
    details = Column(Text, default="")
    data_json = Column(Text, default="{}")
    status = Column(String(40), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

Base.metadata.create_all(bind=engine)
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
class LoginIn(BaseModel):
    email: EmailStr
    password: str
class RecordIn(BaseModel):
    module: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=240)
    details: str = Field(default="", max_length=12000)
    data: dict[str, Any] = Field(default_factory=dict)
    status: str = Field(default="active", max_length=40)
class AdvisorIn(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    crop: Optional[str] = None
    soil_type: Optional[str] = None
    irrigation: Optional[str] = None
    location: Optional[str] = None

def token_for(user: User):
    exp = datetime.now(timezone.utc) + timedelta(hours=24)
    return jwt.encode({"sub": str(user.id), "email": user.email, "exp": exp}, SECRET, algorithm=ALGORITHM)
def public_user(user):
    return {"id": user.id, "name": user.name, "email": user.email}
def current_user(token: Optional[str] = Depends(oauth2), db: Session = Depends(get_db)):
    if not token: raise HTTPException(status_code=401, detail="Sign in to access this resource")
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        uid = int(payload.get("sub", "0"))
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Session expired or invalid")
    user = db.query(User).filter(User.id == uid).first()
    if not user: raise HTTPException(status_code=401, detail="Account not found")
    return user

app = FastAPI(title="Rythu Mitra API", version="1.0.0", description="Agriculture, livestock and farm operations API")
origins = [x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:8080").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

MODULES = [
"farms","plots","crops","crop-calendar","farm-diary","soil-health","water-management","inventory",
"livestock","animal-health","vaccinations","feed-planner","milk-tracking","breeding-calving",
"weather","emergency-alerts","ai-advisor","crop-recommendation","disease-detection","pest-detection",
"fertilizer-planner","smart-irrigation","yield-prediction","expenses-income","profit-analytics",
"market-prices","marketplace","equipment-rental","labour-network","supply-chain","schemes-subsidies",
"insurance","expert-consultation","community","academy","document-vault","iot-sensors",
"satellite-monitoring","digital-twin","voice-assistant","tasks","settings"
]
SCHEME_CATALOG = [
 {"title":"PM-KISAN", "category":"Income support", "description":"Central income-support scheme for eligible landholding farmer families; conditions and exclusions apply.", "authority":"Government of India", "url":"https://pmkisan.gov.in/", "status":"Verify eligibility", "tags":["income","farmer","central"]},
 {"title":"Pradhan Mantri Fasal Bima Yojana (PMFBY)", "category":"Crop insurance", "description":"Crop insurance programme. Availability, notified crops, cut-off dates and premium share vary by season and location.", "authority":"Ministry of Agriculture & Farmers Welfare", "url":"https://pmfby.gov.in/", "status":"Check current season", "tags":["insurance","crop","central"]},
 {"title":"Kisan Credit Card (KCC)", "category":"Agricultural credit", "description":"Credit facility for eligible agriculture and allied activities; bank appraisal and applicable rules apply.", "authority":"Banks / Government of India", "url":"https://www.myscheme.gov.in/", "status":"Check with lender", "tags":["credit","livestock","farm"]},
 {"title":"Soil Health Card", "category":"Soil testing", "description":"Soil testing and nutrient-management support; check the official portal and local agriculture office for current services.", "authority":"Department of Agriculture", "url":"https://soilhealth.dac.gov.in/", "status":"Check local availability", "tags":["soil","nutrients"]},
 {"title":"National Livestock Mission", "category":"Livestock development", "description":"Livestock entrepreneurship and development support under applicable components and current guidelines.", "authority":"Department of Animal Husbandry & Dairying", "url":"https://dahd.gov.in/", "status":"Check current guidelines", "tags":["livestock","dairy","enterprise"]},
 {"title":"Rythu Bharosa / state farmer support", "category":"State agriculture support", "description":"State-level farmer support names, rules and benefits can change. Verify the current Andhra Pradesh or Telangana government programme.", "authority":"State Government", "url":"https://www.myscheme.gov.in/", "status":"Verify current state scheme", "tags":["state","farmer","support"]}
]

@app.get("/")
def root():
    return {"name":"Rythu Mitra API","status":"ok","docs":"/docs","version":"1.0.0"}
@app.get("/api/health")
def health():
    return {"status":"healthy","timestamp":datetime.utcnow().isoformat()+"Z","database":"configured"}

@app.post("/api/auth/register", status_code=201)
def register(body: RegisterIn, db: Session = Depends(get_db)):
    email = body.email.lower()
    if db.query(User).filter(func.lower(User.email) == email).first():
        raise HTTPException(409, "An account with this email already exists")
    user = User(name=body.name.strip(), email=email, password_hash=pwd.hash(body.password))
    db.add(user); db.commit(); db.refresh(user)
    return {"access_token":token_for(user),"token_type":"bearer","user":public_user(user)}
@app.post("/api/auth/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(func.lower(User.email) == body.email.lower()).first()
    if not user or not pwd.verify(body.password, user.password_hash):
        raise HTTPException(401, "Email or password is incorrect")
    return {"access_token":token_for(user),"token_type":"bearer","user":public_user(user)}
@app.get("/api/auth/me")
def me(user: User = Depends(current_user)): return public_user(user)

@app.get("/api/modules")
def modules(): return {"modules":MODULES}
@app.get("/api/records")
def list_records(module: Optional[str] = None, q: Optional[str] = None, limit: int = 250,
                 user: User = Depends(current_user), db: Session = Depends(get_db)):
    query = db.query(Record).filter(Record.owner_id == user.id)
    if module: query = query.filter(Record.module == module)
    if q: query = query.filter((Record.title.ilike(f"%{q}%")) | (Record.details.ilike(f"%{q}%")))
    rows = query.order_by(Record.updated_at.desc()).limit(max(1,min(limit,500))).all()
    return {"items":[serialize_record(r) for r in rows]}
def serialize_record(r):
    try: data = json.loads(r.data_json or "{}")
    except Exception: data = {}
    return {"id":r.id,"module":r.module,"title":r.title,"details":r.details,"data":data,"status":r.status,
            "created_at":r.created_at.isoformat()+"Z" if r.created_at else None,
            "updated_at":r.updated_at.isoformat()+"Z" if r.updated_at else None}
@app.post("/api/records", status_code=201)
def create_record(body: RecordIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if body.module not in MODULES: raise HTTPException(400, "Unknown module")
    r = Record(owner_id=user.id,module=body.module,title=body.title.strip(),details=body.details,
               data_json=json.dumps(body.data),status=body.status)
    db.add(r); db.commit(); db.refresh(r)
    return serialize_record(r)
@app.put("/api/records/{record_id}")
def update_record(record_id: int, body: RecordIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    r = db.query(Record).filter(Record.id==record_id,Record.owner_id==user.id).first()
    if not r: raise HTTPException(404,"Record not found")
    if body.module not in MODULES: raise HTTPException(400,"Unknown module")
    r.module=body.module;r.title=body.title.strip();r.details=body.details;r.data_json=json.dumps(body.data);r.status=body.status
    db.commit();db.refresh(r);return serialize_record(r)
@app.delete("/api/records/{record_id}", status_code=204)
def delete_record(record_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    r=db.query(Record).filter(Record.id==record_id,Record.owner_id==user.id).first()
    if not r: raise HTTPException(404,"Record not found")
    db.delete(r);db.commit();return None

@app.get("/api/dashboard")
def dashboard(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows=db.query(Record).filter(Record.owner_id==user.id).all()
    def count(*mods): return sum(1 for r in rows if r.module in mods)
    def amount(r,key):
        try:return float(json.loads(r.data_json or "{}").get(key,0) or 0)
        except:return 0
    expenses=sum(amount(r,"amount") for r in rows if r.module=="expenses-income" and r.data_json and json.loads(r.data_json or "{}").get("kind")=="expense")
    income=sum(amount(r,"amount") for r in rows if r.module=="expenses-income" and r.data_json and json.loads(r.data_json or "{}").get("kind")=="income")
    return {"farm_plots":count("plots"),"crops":count("crops"),"animals":count("livestock"),"tasks":count("tasks"),
            "records":len(rows),"income":income,"expenses":expenses,"net":income-expenses,
            "recent":[serialize_record(r) for r in sorted(rows,key=lambda x:x.updated_at or datetime.min,reverse=True)[:6]]}

@app.get("/api/schemes")
def schemes(q: Optional[str]=None, category: Optional[str]=None):
    data=SCHEME_CATALOG
    if q:
        q=q.lower();data=[x for x in data if q in (x["title"]+" "+x["description"]+" "+x["category"]+" "+" ".join(x["tags"])).lower()]
    if category: data=[x for x in data if x["category"].lower()==category.lower()]
    return {"items":data,"notice":"Starter catalogue only. Verify eligibility, deadlines and benefits on the linked official source."}

@app.post("/api/advisor")
def advisor(body: AdvisorIn, user: User = Depends(current_user)):
    q=body.question.lower()
    tips=[]
    if any(x in q for x in ["yellow","yellowing","chlorosis"]):
        tips.append("Yellowing has multiple possible causes (nutrient deficiency, waterlogging, pests or disease). Inspect older vs. newer leaves, roots and field moisture; use a soil test before applying nutrients.")
    if any(x in q for x in ["curl","spots","disease","pest","insect","fungus"]):
        tips.append("Inspect several plants and both leaf surfaces. Photograph symptoms with crop, growth stage and location. Confirm with a local agricultural officer or qualified agronomist before treatment.")
    if any(x in q for x in ["water","irrigation","dry","drought"]):
        tips.append("Check root-zone moisture and crop stage before irrigating. Consider forecast rainfall, soil texture and drainage; avoid irrigating solely from a generic schedule.")
    if any(x in q for x in ["cow","cattle","buffalo","milk","animal","calf"]):
        tips.append("For livestock concerns, record temperature, appetite, milk changes and symptoms. Contact a veterinarian promptly for breathing difficulty, bloat, severe weakness, bleeding or inability to stand.")
    if any(x in q for x in ["scheme","subsidy","benefit","pm-kisan"]):
        tips.append("Scheme rules and dates can change. Use the official portal linked in Schemes & Subsidies and confirm eligibility with the relevant department or bank.")
    if not tips:
        tips.append("Share the crop or animal, growth stage/age, location, symptoms, recent weather, soil/water details and a photo if available. Use local expert advice for high-impact decisions.")
    return {"answer":" ".join(tips),"mode":"rule-based safety-first assistant","disclaimer":"This is general guidance, not a diagnosis, guaranteed prediction, veterinary treatment or official eligibility decision."}

@app.post("/api/uploads/metadata")
def upload_metadata(file: UploadFile = File(...), user: User = Depends(current_user)):
    # Deliberately metadata-only in this MVP: secure object storage and malware scanning must be configured for production.
    return {"filename":file.filename,"content_type":file.content_type,"size_limit_bytes":10485760,
            "status":"metadata_received","message":"File storage is not enabled. Configure private object storage and malware scanning before production uploads."}
