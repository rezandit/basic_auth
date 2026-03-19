from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from .auth import verify_password, create_token, verify_token
from . import models, schemas, crud
from .database import engine, Base, get_db, SessionLocal

Base.metadata.create_all(bind=engine)
scheduler = BackgroundScheduler()

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10))
def sync_external_posts(db: Session):
    response = httpx.get("https://jsonplaceholder.typicode.com/posts")
    data = response.json()
    for item in data:
        crud.create_post(db, item["title"], item["body"])
    return data

def fetch_posts_job():
    db = SessionLocal()
    try:
        sync_external_posts(db)
        print("AUTO FETCH SUCCESS")
    finally:
        db.close()

def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No token")
    payload = verify_token(authorization.split(" ")[1])
    if not payload: raise HTTPException(status_code=401, detail="Invalid token")
    return payload

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(fetch_posts_job, "interval", minutes=1)
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    msg = errors[0]["msg"] if errors else "Invalid request"
    return JSONResponse(status_code=422, content={"detail": msg})

@app.post("/users", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_user(db, user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/users", response_model=list[schemas.UserResponse])
def get_users(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return crud.get_users(db)

@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    user = crud.get_user(db, user_id)
    if not user: raise HTTPException(status_code=404, detail="Not found")
    return user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if not crud.delete_user(db, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Deleted"}

@app.post("/login")
def login(data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, data.email)
    if not user: raise HTTPException(status_code=401, detail="User not found")
    if not verify_password(data.password, user.password): raise HTTPException(status_code=401, detail="Wrong password")
    
    token = create_token({"user_id": user.id, "email": user.email})
    return {"access_token": token}

@app.get("/external-posts")
def fetch_external_posts(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    external_data = sync_external_posts(db)
    local_data = crud.get_posts(db)
    return {
        "external_data_total": len(external_data),
        "external_data": external_data,
        "local_data_total": len(local_data),
        "local_data": local_data
    }

@app.get("/posts", response_model=list[schemas.PostResponse])
def get_saved_posts(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return crud.get_posts(db)