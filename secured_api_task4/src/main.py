import os, hmac, hashlib, secrets
from fastapi import FastAPI, Depends, HTTPException, Query, Request, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
from .database import Base, engine, get_db
from .models import Customer
from .schemas import CustomerCreate, CustomerUpdate, CustomerOut
from .auth import require_api_key

load_dotenv()
Base.metadata.create_all(bind=engine)
app = FastAPI(title="Secured Customer API")

def process_order_event(payload: bytes):
    # Replace with durable queue/database processing in production.
    print(f"Processed order event ({len(payload)} bytes)")

@app.post("/customers", response_model=CustomerOut, status_code=201, dependencies=[Depends(require_api_key)])
def create_customer(data: CustomerCreate, db: Session = Depends(get_db)):
    customer = Customer(name=data.name, email=str(data.email))
    db.add(customer)
    try:
        db.commit()
        db.refresh(customer)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already exists")
    return customer

@app.get("/customers", response_model=list[CustomerOut], dependencies=[Depends(require_api_key)])
def list_customers(page: int = Query(1, ge=1), per_page: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    return db.query(Customer).order_by(Customer.id).offset((page - 1) * per_page).limit(per_page).all()

@app.get("/customers/{customer_id}", response_model=CustomerOut, dependencies=[Depends(require_api_key)])
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@app.put("/customers/{customer_id}", response_model=CustomerOut, dependencies=[Depends(require_api_key)])
def update_customer(customer_id: int, data: CustomerUpdate, db: Session = Depends(get_db)):
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    customer.name, customer.email = data.name, str(data.email)
    try:
        db.commit()
        db.refresh(customer)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already exists")
    return customer

@app.delete("/customers/{customer_id}", status_code=204, dependencies=[Depends(require_api_key)])
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(customer)
    db.commit()

@app.post("/webhooks/order-events", status_code=200)
async def order_webhook(request: Request, background_tasks: BackgroundTasks, x_signature: str | None = None):
    # Header is read explicitly so the raw bytes are signed exactly as received.
    signature = request.headers.get("X-Signature")
    body = await request.body()
    secret = os.getenv("WEBHOOK_SECRET", "dev-webhook-secret").encode()
    expected = hmac.new(secret, body, hashlib.sha256).hexdigest()
    if not signature or not hmac.compare_digest(signature, expected):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    background_tasks.add_task(process_order_event, body)
    return {"status": "accepted"}

@app.post("/oauth/token")
def oauth_token(request: dict):
    client_id = os.getenv("OAUTH_CLIENT_ID", "demo-client")
    client_secret = os.getenv("OAUTH_CLIENT_SECRET", "demo-secret")
    if request.get("client_id") != client_id or request.get("client_secret") != client_secret:
        raise HTTPException(status_code=401, detail="Invalid client credentials")
    return {"access_token": "demo-access-token", "token_type": "bearer", "expires_in": 3600}
