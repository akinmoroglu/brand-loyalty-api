from sqlalchemy import Column, String, DateTime, Index, ForeignKey
from datetime import datetime, timezone
from app.db.base import Base


class BrandCustomer(Base):
    """Many-to-many relationship between brands and customers"""
    __tablename__ = "brand_customers"

    id = Column(String, primary_key=True)  # Composite: brand_id:phone_number
    brand_id = Column(String, ForeignKey("brands.id"), nullable=False)
    phone_number = Column(String(10), ForeignKey("customers.phone_number"), nullable=False)
    brand_customer_id = Column(String, nullable=False)  # Brand's custom customer ID
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        # Ensure brand can't assign same customer ID twice
        Index('idx_brand_customer_id', 'brand_id', 'brand_customer_id', unique=True),
        # Ensure same customer can't be registered twice with same brand
        Index('idx_brand_phone', 'brand_id', 'phone_number', unique=True),
    )
