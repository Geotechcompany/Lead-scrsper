from pydantic import BaseModel, EmailStr
from typing import Optional

class LeadCreate(BaseModel):
    name: Optional[str] = None
    email: EmailStr
    company: Optional[str] = None
    website: Optional[str] = None
    notes: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None

class LeadOut(BaseModel):
    id: int
    name: Optional[str]
    email: EmailStr
    company: Optional[str]
    website: Optional[str]
    notes: Optional[str]
    city: Optional[str]
    state: Optional[str]
    status: str

    class Config:
        from_attributes = True

class CampaignCreate(BaseModel):
    name: str
    subject_template: str
    body_template: str
    model_preset: Optional[str] = None

class CampaignOut(BaseModel):
    id: int
    name: str
    subject_template: str
    body_template: str
    model_preset: Optional[str]

    class Config:
        from_attributes = True
