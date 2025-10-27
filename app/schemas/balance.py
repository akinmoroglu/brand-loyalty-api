from pydantic import BaseModel
from datetime import datetime


class BalanceResponse(BaseModel):
    brandId: str
    userId: str
    points: int
    updatedAt: datetime

    class Config:
        from_attributes = True
