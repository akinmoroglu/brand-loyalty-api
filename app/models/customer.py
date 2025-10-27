from sqlalchemy import Column, String, DateTime
from datetime import datetime, timezone
from app.db.base import Base


class Customer(Base):
    """Customer model - identified by Turkish phone number"""
    __tablename__ = "customers"

    phone_number = Column(String(10), primary_key=True)  # 10-digit Turkish phone
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
