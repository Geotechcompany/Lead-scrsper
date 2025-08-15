from fastapi import FastAPI, Depends, Response, Request, HTTPException
from fastapi.responses import StreamingResponse, RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import select
from .db import Base, engine, get_db
from .models import Lead, Campaign, EmailLog, Unsubscribe
from .schemas import LeadCreate, LeadOut, CampaignCreate, CampaignOut
from .scheduler import start_scheduler
from .config import settings
import io, datetime

app = FastAPI(title="LeadGen System")

@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    start_scheduler()

@app.get("/", response_class=HTMLResponse)
async def home():
    return "<h2>LeadGen System</h2><p>See <a href='/docs'>/docs</a> for API.</p>"

# Leads
@app.post("/leads", response_model=LeadOut)
async def create_lead(payload: LeadCreate, db: Session = Depends(get_db)):
    # skip if unsubscribed
    if db.query(Unsubscribe).filter(Unsubscribe.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email is unsubscribed")
    lead = Lead(**payload.model_dump())
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead

@app.get("/leads", response_model=list[LeadOut])
async def list_leads(db: Session = Depends(get_db)):
    leads = db.execute(select(Lead).order_by(Lead.id.desc())).scalars().all()
    return leads

# Campaigns
@app.post("/campaigns", response_model=CampaignOut)
async def create_campaign(payload: CampaignCreate, db: Session = Depends(get_db)):
    c = Campaign(**payload.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c

@app.get("/campaigns", response_model=list[CampaignOut])
async def list_campaigns(db: Session = Depends(get_db)):
    cs = db.execute(select(Campaign).order_by(Campaign.id.desc())).scalars().all()
    return cs

# Tracking pixel
@app.get("/t/pixel/{token}.png")
async def tracking_pixel(token: str, db: Session = Depends(get_db)):
    log = db.query(EmailLog).filter(EmailLog.token == token).first()
    if log and not log.opened:
        log.opened = True
        log.opened_at = datetime.datetime.utcnow()
        db.add(log); db.commit()
    # return 1x1 transparent PNG
    return StreamingResponse(io.BytesIO(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0cIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\x0d\n\x2d\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    ), media_type="image/png")

# Click tracking redirect (to your calendar/site)
@app.get("/t/click/{token}")
async def tracking_click(token: str, db: Session = Depends(get_db)):
    log = db.query(EmailLog).filter(EmailLog.token == token).first()
    if log and not log.clicked:
        log.clicked = True
        log.clicked_at = datetime.datetime.utcnow()
        db.add(log); db.commit()
    # Redirect to your calendly or website contact page
    return RedirectResponse(url="https://calendly.com/")

@app.get("/unsubscribe")
async def unsubscribe(email: str, db: Session = Depends(get_db)):
    if not email:
        return HTMLResponse("<p>Missing email.</p>")
    if not db.query(Unsubscribe).filter(Unsubscribe.email == email).first():
        db.add(Unsubscribe(email=email))
        # Also mark existing lead as unsubscribed
        lead = db.query(Lead).filter(Lead.email == email).first()
        if lead:
            lead.status = "unsubscribed"
            db.add(lead)
        db.commit()
    return HTMLResponse("<p>You have been unsubscribed. Sorry to see you go.</p>")
