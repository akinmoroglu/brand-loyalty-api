from pydantic import BaseModel, Field


class EarnRequest(BaseModel):
    customerId: str = Field(..., description="Brand's custom customer ID")
    points: int = Field(..., gt=0)
    txnId: str


class RedeemRequest(BaseModel):
    customerId: str = Field(..., description="Brand's custom customer ID")
    points: int
    txnId: str
    provisionId: str


class VoidRequest(BaseModel):
    txnId: str


class TransactionResponse(BaseModel):
    status: str
    txnId: str
    brandId: str
    customerId: str
    phoneNumber: str
    points: int
    updatedAt: str

    class Config:
        from_attributes = True
