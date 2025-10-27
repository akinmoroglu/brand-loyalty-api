from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime, timezone
from app.db.base import Base


class Provision(Base):
    __tablename__ = "provisions"

    provision_id = Column(String, primary_key=True)
    brand_id = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    points = Column(Integer, nullable=False)  # Original provisioned points
    remaining_points = Column(Integer, nullable=False)  # Points still available
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
