from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.db.session import get_db
from app.core.crud import BalanceCRUD, ProvisionCRUD, BrandCustomerCRUD, BrandCRUD
from app.schemas import ProvisionRequest

router = APIRouter()


@router.post("/brands/{brand_id}/provision")
def create_provision(brand_id: str, body: ProvisionRequest, db: Session = Depends(get_db)):
    """Create a provision (reserve and lock points for later redemption) using brand's customer ID"""
    # Validate brand exists
    brand = BrandCRUD.get_by_id(db, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail=f"Brand '{brand_id}' not found")

    # Check if provision ID already exists
    existing_provision = ProvisionCRUD.get_by_id(db, body.provisionId)
    if existing_provision:
        raise HTTPException(status_code=409, detail=f"Provision ID '{body.provisionId}' already exists")

    # Get customer by brand customer ID
    brand_customer = BrandCustomerCRUD.get_by_brand_customer_id(db, brand_id, body.customerId)
    if not brand_customer:
        raise HTTPException(status_code=404, detail=f"Customer '{body.customerId}' not found for this brand")

    phone_number = brand_customer.phone_number

    # Get current balance (using brandCustomerId as user_id)
    balance = BalanceCRUD.get_or_create(db, brand_id, body.customerId)

    if balance.points < body.points:
        raise HTTPException(status_code=400, detail="Insufficient points to provision")

    # LOCK POINTS: Deduct points from balance when provisioning
    balance = BalanceCRUD.update_points(db, balance, -body.points)

    # Ensure expiresAt has timezone info
    expires_at = body.expiresAt
    if expires_at.tzinfo is None:
        # If naive datetime, assume UTC
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    # Create provision (using brandCustomerId as user_id)
    ProvisionCRUD.create(db, body.provisionId, brand_id, body.customerId, body.points, expires_at)

    return {
        "status": "provisioned",
        "provisionId": body.provisionId,
        "customerId": body.customerId,
        "phoneNumber": phone_number,
        "provisionedPoints": body.points,
        "remainingBalance": balance.points,
        "expiresAt": body.expiresAt.isoformat()
    }


@router.get("/provisions/{provision_id}")
def check_provision(provision_id: str, db: Session = Depends(get_db)):
    """Check status of a provision"""
    provision = ProvisionCRUD.get_by_id(db, provision_id)
    if not provision:
        raise HTTPException(status_code=404, detail="Provision not found")

    now = datetime.now(timezone.utc)
    if now > provision.expires_at:
        return JSONResponse(
            status_code=410,
            content={"status": "expired", "provisionId": provision_id}
        )

    return {
        "status": "active",
        "provisionId": provision.provision_id,
        "userId": provision.user_id,
        "brandId": provision.brand_id,
        "points": provision.points,
        "expiresAt": provision.expires_at.isoformat()
    }


@router.post("/webhooks/loyalty", status_code=204)
def webhook(event: dict):
    """Webhook endpoint for loyalty events"""
    # In real implementation, verify and process the webhook
    print("Received webhook:", event)
    return
