from sqlalchemy import Column, String, Integer, DateTime, Index
from datetime import datetime, timezone
from app.db.base import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True)  # Composite: brand_id:txn_id
    txn_id = Column(String, nullable=False)  # Brand's transaction ID
    brand_id = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    points = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        # Ensure transaction ID is unique per brand (not globally)
        Index('idx_brand_txn', 'brand_id', 'txn_id', unique=True),
    )
