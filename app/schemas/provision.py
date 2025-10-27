from pydantic import BaseModel, Field
from datetime import datetime


class ProvisionRequest(BaseModel):
    customerId: str = Field(..., description="Brand's custom customer ID")
    points: int
    provisionId: str
    expiresAt: datetime


class ProvisionResponse(BaseModel):
    status: str
    provisionId: str
    customerId: str
    phoneNumber: str
    brandId: str
    points: int
    expiresAt: datetime

    class Config:
        from_attributes = True
