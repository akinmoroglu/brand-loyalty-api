from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.db.session import get_db
from app.core.crud import BalanceCRUD, TransactionCRUD, ProvisionCRUD, BrandCustomerCRUD, BrandCRUD
from app.schemas import EarnRequest, RedeemRequest, VoidRequest

router = APIRouter()


@router.post("/brands/{brand_id}/earn")
def earn_points(brand_id: str, body: EarnRequest, db: Session = Depends(get_db)):
    """Add points to a customer's balance using brand's customer ID"""
    # Validate brand exists
    brand = BrandCRUD.get_by_id(db, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail=f"Brand '{brand_id}' not found")

    # Get customer by brand customer ID
    brand_customer = BrandCustomerCRUD.get_by_brand_customer_id(db, brand_id, body.customerId)
    if not brand_customer:
        raise HTTPException(status_code=404, detail=f"Customer '{body.customerId}' not found for this brand")

    # Check if transaction already exists for this brand
    if TransactionCRUD.get_by_id(db, brand_id, body.txnId):
        raise HTTPException(status_code=409, detail=f"Transaction ID '{body.txnId}' already used for this brand")

    phone_number = brand_customer.phone_number

    # Get or create balance (using brandCustomerId as user_id)
    balance = BalanceCRUD.get_or_create(db, brand_id, body.customerId)

    # Update balance
    balance = BalanceCRUD.update_points(db, balance, body.points)

    # Create transaction record (using brandCustomerId as user_id)
    TransactionCRUD.create(db, body.txnId, brand_id, body.customerId, body.points)

    return {
        "status": "earned",
        "txnId": body.txnId,
        "brandId": brand_id,
        "customerId": body.customerId,
        "phoneNumber": phone_number,
        "points": balance.points,
        "updatedAt": balance.updated_at.isoformat()
    }


@router.post("/brands/{brand_id}/redeem")
def redeem_points(brand_id: str, body: RedeemRequest, db: Session = Depends(get_db)):
    """Redeem points from a customer's balance using brand's customer ID"""
    # Validate brand exists
    brand = BrandCRUD.get_by_id(db, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail=f"Brand '{brand_id}' not found")

    # Get customer by brand customer ID
    brand_customer = BrandCustomerCRUD.get_by_brand_customer_id(db, brand_id, body.customerId)
    if not brand_customer:
        raise HTTPException(status_code=404, detail=f"Customer '{body.customerId}' not found for this brand")

    phone_number = brand_customer.phone_number

    # Check if transaction already exists for this brand
    if TransactionCRUD.get_by_id(db, brand_id, body.txnId):
        raise HTTPException(status_code=409, detail=f"Transaction ID '{body.txnId}' already used for this brand")

    # Get provision
    provision = ProvisionCRUD.get_by_id(db, body.provisionId)
    if not provision:
        raise HTTPException(status_code=404, detail="Provision not found")

    # Check if expired
    now = datetime.now(timezone.utc)
    # Ensure provision expires_at is timezone-aware for comparison
    expires_at = provision.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if now > expires_at:
        raise HTTPException(status_code=410, detail="Provision expired")

    # Validate provision matches user and brand (using brandCustomerId)
    if provision.user_id != body.customerId or provision.brand_id != brand_id:
        raise HTTPException(status_code=400, detail="Provision details mismatch")

    # Check if provision has enough remaining points for this redemption
    if provision.remaining_points < body.points:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient provisioned points. Requested: {body.points}, Available: {provision.remaining_points}"
        )

    # Points are already locked in provision, don't deduct from balance again
    # Just update the provision's remaining points
    provision = ProvisionCRUD.update_remaining_points(db, provision, body.points)

    # Create transaction record (using brandCustomerId as user_id)
    TransactionCRUD.create(db, body.txnId, brand_id, body.customerId, -body.points)

    # Remove provision only if fully used
    provision_status = "fully_redeemed" if provision.remaining_points == 0 else "partially_redeemed"
    if provision.remaining_points == 0:
        ProvisionCRUD.delete(db, provision)

    # Get updated balance (using brandCustomerId as user_id)
    balance = BalanceCRUD.get_or_create(db, brand_id, body.customerId)

    return {
        "status": "redeemed",
        "txnId": body.txnId,
        "brandId": brand_id,
        "customerId": body.customerId,
        "phoneNumber": phone_number,
        "redeemedPoints": body.points,
        "provisionStatus": provision_status,
        "remainingProvisionPoints": provision.remaining_points if provision.remaining_points > 0 else 0,
        "currentBalance": balance.points,
        "updatedAt": balance.updated_at.isoformat()
    }


@router.post("/brands/{brand_id}/void")
def void_transaction(brand_id: str, body: VoidRequest, db: Session = Depends(get_db)):
    """Void/reverse a transaction"""
    # Get transaction for this brand
    txn = TransactionCRUD.get_by_id(db, brand_id, body.txnId)
    if not txn:
        raise HTTPException(status_code=404, detail=f"Transaction '{body.txnId}' not found for this brand")

    # Reverse the points
    balance = BalanceCRUD.get_or_create(db, txn.brand_id, txn.user_id)
    BalanceCRUD.update_points(db, balance, -txn.points)

    # Delete transaction
    TransactionCRUD.delete(db, txn)

    return {
        "voided": True,
        "txnId": body.txnId,
        "status": "reversed"
    }
