from sqlalchemy import Column, String, DateTime
from datetime import datetime, timezone
from app.db.base import Base


class Brand(Base):
    __tablename__ = "brands"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
