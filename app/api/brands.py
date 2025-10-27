from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.core.crud import BrandCRUD
from app.schemas import BrandCreate, BrandResponse

router = APIRouter()


@router.get("", response_model=List[BrandResponse])
def list_brands(db: Session = Depends(get_db)):
    """Get all brands"""
    brands = BrandCRUD.get_all(db)
    return brands


@router.post("", response_model=BrandResponse, status_code=201)
def create_brand(brand: BrandCreate, db: Session = Depends(get_db)):
    """Create a new brand"""
    # Check if brand already exists
    existing = BrandCRUD.get_by_id(db, brand.id)
    if existing:
        raise HTTPException(status_code=409, detail="Brand ID already exists")

    return BrandCRUD.create(db, brand.id, brand.name)


@router.get("/{brand_id}", response_model=BrandResponse)
def get_brand(brand_id: str, db: Session = Depends(get_db)):
    """Get a specific brand"""
    brand = BrandCRUD.get_by_id(db, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand
