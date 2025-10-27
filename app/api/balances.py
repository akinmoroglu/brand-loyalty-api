from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.crud import BalanceCRUD, BrandCustomerCRUD, BrandCRUD

router = APIRouter()


@router.get("/brands/{brand_id}/customers/{customer_id}/balance")
def get_balance(brand_id: str, customer_id: str, db: Session = Depends(get_db)):
    """Get balance for a customer at a specific brand using brand's customer ID"""
    # Validate brand exists
    brand = BrandCRUD.get_by_id(db, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail=f"Brand '{brand_id}' not found")

    # Get customer by brand customer ID
    brand_customer = BrandCustomerCRUD.get_by_brand_customer_id(db, brand_id, customer_id)
    if not brand_customer:
        raise HTTPException(status_code=404, detail=f"Customer '{customer_id}' not found for this brand")

    phone_number = brand_customer.phone_number
    # Use brandCustomerId as user_id to match transactions
    balance = BalanceCRUD.get_or_create(db, brand_id, customer_id)

    return {
        "brandId": balance.brand_id,
        "customerId": customer_id,
        "phoneNumber": phone_number,
        "points": balance.points,
        "updatedAt": balance.updated_at.isoformat()
    }
