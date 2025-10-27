from sqlalchemy import Column, String, Integer, DateTime, Index
from datetime import datetime, timezone
from app.db.base import Base


class Balance(Base):
    __tablename__ = "balances"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    points = Column(Integer, default=0)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index('idx_brand_user', 'brand_id', 'user_id', unique=True),
    )
