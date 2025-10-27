from pydantic import BaseModel, Field, field_validator
import re


class CustomerCreate(BaseModel):
    phoneNumber: str = Field(..., min_length=10, max_length=10, description="10-digit Turkish phone number")

    @field_validator('phoneNumber')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r'^\d{10}$', v):
            raise ValueError('Phone number must be exactly 10 digits')
        return v


class CustomerResponse(BaseModel):
    phoneNumber: str

    class Config:
        from_attributes = True


class BrandCustomerCreate(BaseModel):
    phoneNumber: str = Field(..., min_length=10, max_length=10)
    brandCustomerId: str = Field(..., min_length=1, description="Brand's custom customer ID")

    @field_validator('phoneNumber')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r'^\d{10}$', v):
            raise ValueError('Phone number must be exactly 10 digits')
        return v


class BrandCustomerResponse(BaseModel):
    phoneNumber: str
    brandId: str
    brandCustomerId: str

    class Config:
        from_attributes = True


class BrandCustomerDetail(BaseModel):
    phoneNumber: str
    brandCustomerId: str
    points: int
    createdAt: str

    class Config:
        from_attributes = True
