from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Boolean, UniqueConstraint, func
from .db import Base

class Lead(Base):
    __tablename__ = "leads"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    website: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(128), nullable=True)
    state: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped = mapped_column(DateTime(timezone=True), server_default=func.now())

    status: Mapped[str] = mapped_column(String(32), default="new")  # new, emailed, replied, bounced, unsubscribed

    __table_args__ = (UniqueConstraint('email', name='uq_leads_email'),)

class Campaign(Base):
    __tablename__ = "campaigns"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    subject_template: Mapped[str] = mapped_column(String(255), nullable=False)
    body_template: Mapped[str] = mapped_column(Text, nullable=False)
    model_preset: Mapped[str | None] = mapped_column(String(64), nullable=True)  # e.g., "mistral"
    created_at: Mapped = mapped_column(DateTime(timezone=True), server_default=func.now())

class EmailLog(Base):
    __tablename__ = "email_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lead_id: Mapped[int] = mapped_column(Integer, ForeignKey("leads.id"))
    campaign_id: Mapped[int] = mapped_column(Integer, ForeignKey("campaigns.id"))
    message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sent_at: Mapped = mapped_column(DateTime(timezone=True), server_default=func.now())
    opened: Mapped[bool] = mapped_column(Boolean, default=False)
    opened_at: Mapped = mapped_column(DateTime(timezone=True), nullable=True)
    clicked: Mapped[bool] = mapped_column(Boolean, default=False)
    clicked_at: Mapped = mapped_column(DateTime(timezone=True), nullable=True)
    reply_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    reply_at: Mapped = mapped_column(DateTime(timezone=True), nullable=True)
    token: Mapped[str] = mapped_column(String(64), index=True)

class Unsubscribe(Base):
    __tablename__ = "unsubscribes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    created_at: Mapped = mapped_column(DateTime(timezone=True), server_default=func.now())
