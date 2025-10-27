from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.core.crud import BrandCustomerCRUD, BalanceCRUD, BrandCRUD
from app.schemas import BrandCustomerCreate, BrandCustomerDetail

router = APIRouter()


@router.post("/brands/{brand_id}/customers", response_model=BrandCustomerDetail, status_code=201)
def register_customer(
    brand_id: str,
    body: BrandCustomerCreate,
    db: Session = Depends(get_db)
):
    """Register a customer to a brand with brand-specific customer ID"""

    # Validate brand exists
    brand = BrandCRUD.get_by_id(db, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail=f"Brand '{brand_id}' not found")

    # Check if customer already registered with this brand
    existing = BrandCustomerCRUD.get_by_phone(db, brand_id, body.phoneNumber)
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Customer with phone {body.phoneNumber} already registered to this brand"
        )

    # Check if brand customer ID already used
    existing_id = BrandCustomerCRUD.get_by_brand_customer_id(db, brand_id, body.brandCustomerId)
    if existing_id:
        raise HTTPException(
            status_code=409,
            detail=f"Brand customer ID '{body.brandCustomerId}' already exists"
        )

    # Create brand-customer relationship
    brand_customer = BrandCustomerCRUD.create(db, brand_id, body.phoneNumber, body.brandCustomerId)

    # Get or create balance for this customer (using brandCustomerId as user_id)
    balance = BalanceCRUD.get_or_create(db, brand_id, body.brandCustomerId)

    return {
        "phoneNumber": brand_customer.phone_number,
        "brandCustomerId": brand_customer.brand_customer_id,
        "points": balance.points,
        "createdAt": brand_customer.created_at.isoformat()
    }


@router.get("/brands/{brand_id}/customers", response_model=List[BrandCustomerDetail])
def list_customers(brand_id: str, db: Session = Depends(get_db)):
    """List all customers of a brand with their details"""

    # Validate brand exists
    brand = BrandCRUD.get_by_id(db, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail=f"Brand '{brand_id}' not found")

    brand_customers = BrandCustomerCRUD.list_by_brand(db, brand_id)

    results = []
    for bc in brand_customers:
        # Get balance for each customer (using brandCustomerId as user_id)
        balance = BalanceCRUD.get_or_create(db, brand_id, bc.brand_customer_id)
        results.append({
            "phoneNumber": bc.phone_number,
            "brandCustomerId": bc.brand_customer_id,
            "points": balance.points,
            "createdAt": bc.created_at.isoformat()
        })

    return results


@router.get("/brands/{brand_id}/customers/{brand_customer_id}", response_model=BrandCustomerDetail)
def get_customer(brand_id: str, brand_customer_id: str, db: Session = Depends(get_db)):
    """Get a specific customer by their brand-specific customer ID"""

    # Validate brand exists
    brand = BrandCRUD.get_by_id(db, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail=f"Brand '{brand_id}' not found")

    brand_customer = BrandCustomerCRUD.get_by_brand_customer_id(db, brand_id, brand_customer_id)
    if not brand_customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    balance = BalanceCRUD.get_or_create(db, brand_id, brand_customer.brand_customer_id)

    return {
        "phoneNumber": brand_customer.phone_number,
        "brandCustomerId": brand_customer.brand_customer_id,
        "points": balance.points,
        "createdAt": brand_customer.created_at.isoformat()
    }


@router.get("/brands/{brand_id}/customers/by-phone/{phone_number}", response_model=BrandCustomerDetail)
def get_customer_by_phone(brand_id: str, phone_number: str, db: Session = Depends(get_db)):
    """Check if a customer with given phone number is registered with the brand"""

    # Validate brand exists
    brand = BrandCRUD.get_by_id(db, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail=f"Brand '{brand_id}' not found")

    # Validate phone number format (10 digits)
    if len(phone_number) != 10 or not phone_number.isdigit():
        raise HTTPException(status_code=400, detail="Phone number must be exactly 10 digits")

    # Check if customer is registered with this brand
    brand_customer = BrandCustomerCRUD.get_by_phone(db, brand_id, phone_number)
    if not brand_customer:
        raise HTTPException(
            status_code=404,
            detail=f"Customer with phone {phone_number} is not registered with this brand"
        )

    balance = BalanceCRUD.get_or_create(db, brand_id, brand_customer.brand_customer_id)

    return {
        "phoneNumber": brand_customer.phone_number,
        "brandCustomerId": brand_customer.brand_customer_id,
        "points": balance.points,
        "createdAt": brand_customer.created_at.isoformat()
    }
