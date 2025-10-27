from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional, List
from app.models import Brand, Balance, Transaction, Provision, Customer, BrandCustomer


class BrandCRUD:
    @staticmethod
    def get_all(db: Session) -> List[Brand]:
        """Get all brands"""
        return db.query(Brand).all()

    @staticmethod
    def get_by_id(db: Session, brand_id: str) -> Optional[Brand]:
        """Get brand by ID"""
        return db.query(Brand).filter(Brand.id == brand_id).first()

    @staticmethod
    def create(db: Session, brand_id: str, name: str) -> Brand:
        """Create a new brand"""
        brand = Brand(id=brand_id, name=name)
        db.add(brand)
        db.commit()
        db.refresh(brand)
        return brand


class BalanceCRUD:
    @staticmethod
    def get_or_create(db: Session, brand_id: str, user_id: str) -> Balance:
        """Get or create balance for brand and user"""
        balance = db.query(Balance).filter(
            Balance.brand_id == brand_id,
            Balance.user_id == user_id
        ).first()

        if not balance:
            balance = Balance(brand_id=brand_id, user_id=user_id, points=0)
            db.add(balance)
            db.commit()
            db.refresh(balance)

        return balance

    @staticmethod
    def update_points(db: Session, balance: Balance, points_delta: int) -> Balance:
        """Update balance points"""
        balance.points += points_delta
        balance.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(balance)
        return balance


class TransactionCRUD:
    @staticmethod
    def get_by_id(db: Session, brand_id: str, txn_id: str) -> Optional[Transaction]:
        """Get transaction by brand and transaction ID"""
        return db.query(Transaction).filter(
            Transaction.brand_id == brand_id,
            Transaction.txn_id == txn_id
        ).first()

    @staticmethod
    def create(db: Session, txn_id: str, brand_id: str, user_id: str, points: int) -> Transaction:
        """Create a new transaction"""
        # Create composite ID
        composite_id = f"{brand_id}:{txn_id}"
        txn = Transaction(
            id=composite_id,
            txn_id=txn_id,
            brand_id=brand_id,
            user_id=user_id,
            points=points
        )
        db.add(txn)
        db.commit()
        db.refresh(txn)
        return txn

    @staticmethod
    def delete(db: Session, txn: Transaction) -> None:
        """Delete a transaction"""
        db.delete(txn)
        db.commit()


class ProvisionCRUD:
    @staticmethod
    def get_by_id(db: Session, provision_id: str) -> Optional[Provision]:
        """Get provision by ID"""
        return db.query(Provision).filter(Provision.provision_id == provision_id).first()

    @staticmethod
    def create(db: Session, provision_id: str, brand_id: str, user_id: str,
               points: int, expires_at: datetime) -> Provision:
        """Create a new provision"""
        provision = Provision(
            provision_id=provision_id,
            brand_id=brand_id,
            user_id=user_id,
            points=points,
            remaining_points=points,  # Initially, remaining = total
            expires_at=expires_at
        )
        db.add(provision)
        db.commit()
        db.refresh(provision)
        return provision

    @staticmethod
    def update_remaining_points(db: Session, provision: Provision, points_used: int) -> Provision:
        """Update remaining points after partial redemption"""
        provision.remaining_points -= points_used
        db.commit()
        db.refresh(provision)
        return provision

    @staticmethod
    def delete(db: Session, provision: Provision) -> None:
        """Delete a provision"""
        db.delete(provision)
        db.commit()


class CustomerCRUD:
    @staticmethod
    def get_or_create(db: Session, phone_number: str) -> Customer:
        """Get or create customer by phone number"""
        customer = db.query(Customer).filter(Customer.phone_number == phone_number).first()

        if not customer:
            customer = Customer(phone_number=phone_number)
            db.add(customer)
            db.commit()
            db.refresh(customer)

        return customer

    @staticmethod
    def get_by_phone(db: Session, phone_number: str) -> Optional[Customer]:
        """Get customer by phone number"""
        return db.query(Customer).filter(Customer.phone_number == phone_number).first()


class BrandCustomerCRUD:
    @staticmethod
    def create(db: Session, brand_id: str, phone_number: str, brand_customer_id: str) -> BrandCustomer:
        """Register a customer to a brand"""
        # Ensure customer exists
        CustomerCRUD.get_or_create(db, phone_number)

        # Create brand-customer relationship
        id_key = f"{brand_id}:{phone_number}"
        brand_customer = BrandCustomer(
            id=id_key,
            brand_id=brand_id,
            phone_number=phone_number,
            brand_customer_id=brand_customer_id
        )
        db.add(brand_customer)
        db.commit()
        db.refresh(brand_customer)
        return brand_customer

    @staticmethod
    def get_by_brand_customer_id(db: Session, brand_id: str, brand_customer_id: str) -> Optional[BrandCustomer]:
        """Get brand-customer by brand's custom customer ID"""
        return db.query(BrandCustomer).filter(
            BrandCustomer.brand_id == brand_id,
            BrandCustomer.brand_customer_id == brand_customer_id
        ).first()

    @staticmethod
    def get_by_phone(db: Session, brand_id: str, phone_number: str) -> Optional[BrandCustomer]:
        """Get brand-customer by phone number"""
        return db.query(BrandCustomer).filter(
            BrandCustomer.brand_id == brand_id,
            BrandCustomer.phone_number == phone_number
        ).first()

    @staticmethod
    def list_by_brand(db: Session, brand_id: str) -> List[BrandCustomer]:
        """List all customers of a brand"""
        return db.query(BrandCustomer).filter(BrandCustomer.brand_id == brand_id).all()
