from pydantic import BaseModel


class BrandCreate(BaseModel):
    id: str
    name: str


class BrandResponse(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True
