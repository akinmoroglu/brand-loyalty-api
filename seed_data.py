"""
Database Seed Script
Populates the database with realistic test data for developers
"""
from datetime import datetime, timezone, timedelta
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models.brand import Brand
from app.models.customer import Customer
from app.models.brand_customer import BrandCustomer
from app.models.balance import Balance
from app.models.transaction import Transaction
from app.models.provision import Provision


def clear_database():
    """Clear all data from database"""
    print("Clearing existing data...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database cleared and recreated.")


def seed_brands(db):
    """Create test brands"""
    print("\nSeeding brands...")
    brands = [
        Brand(
            id="brand-001",
            name="Coffee World"
        ),
        Brand(
            id="brand-002",
            name="BookStore Plus"
        ),
        Brand(
            id="brand-003",
            name="FitLife Gym"
        )
    ]

    for brand in brands:
        db.add(brand)
    db.commit()
    print(f"✓ Created {len(brands)} brands")
    return brands


def seed_customers(db, brands):
    """Create test customers and brand-customer relationships"""
    print("\nSeeding customers...")

    # Customer data: phone_number, name (for reference)
    customer_data = [
        ("5551234567", "Ahmet Yılmaz"),
        ("5559876543", "Ayşe Demir"),
        ("5555554444", "Mehmet Çelik"),
        ("5552223333", "Fatma Kaya"),
        ("5557778888", "Can Özdemir"),
    ]

    customers_created = 0
    relationships_created = 0

    # Create customers
    for phone, name in customer_data:
        customer = Customer(phone_number=phone)
        db.add(customer)
        customers_created += 1
    db.commit()
    print(f"✓ Created {customers_created} customers")

    # Create brand-customer relationships
    # Customer 1: Member of all three brands
    brand_customers = [
        BrandCustomer(
            id=f"{brands[0].id}:5551234567",
            brand_id=brands[0].id,
            phone_number="5551234567",
            brand_customer_id="CW-1001"
        ),
        BrandCustomer(
            id=f"{brands[1].id}:5551234567",
            brand_id=brands[1].id,
            phone_number="5551234567",
            brand_customer_id="BS-2001"
        ),
        BrandCustomer(
            id=f"{brands[2].id}:5551234567",
            brand_id=brands[2].id,
            phone_number="5551234567",
            brand_customer_id="FL-3001"
        ),

        # Customer 2: Member of Coffee World and BookStore
        BrandCustomer(
            id=f"{brands[0].id}:5559876543",
            brand_id=brands[0].id,
            phone_number="5559876543",
            brand_customer_id="CW-1002"
        ),
        BrandCustomer(
            id=f"{brands[1].id}:5559876543",
            brand_id=brands[1].id,
            phone_number="5559876543",
            brand_customer_id="BS-2002"
        ),

        # Customer 3: Member of Coffee World only
        BrandCustomer(
            id=f"{brands[0].id}:5555554444",
            brand_id=brands[0].id,
            phone_number="5555554444",
            brand_customer_id="CW-1003"
        ),

        # Customer 4: Member of BookStore only
        BrandCustomer(
            id=f"{brands[1].id}:5552223333",
            brand_id=brands[1].id,
            phone_number="5552223333",
            brand_customer_id="BS-2003"
        ),

        # Customer 5: Member of FitLife only
        BrandCustomer(
            id=f"{brands[2].id}:5557778888",
            brand_id=brands[2].id,
            phone_number="5557778888",
            brand_customer_id="FL-3002"
        ),
    ]

    for bc in brand_customers:
        db.add(bc)
        relationships_created += 1
    db.commit()
    print(f"✓ Created {relationships_created} brand-customer relationships")

    return brand_customers


def seed_transactions_and_balances(db, brands, brand_customers):
    """Create test transactions and calculate balances"""
    print("\nSeeding transactions and balances...")

    transactions = [
        # Coffee World transactions
        ("brand-001", "CW-1001", 100, "TXN-CW-001"),  # Ahmet: 100 points
        ("brand-001", "CW-1001", 50, "TXN-CW-002"),   # Ahmet: +50 = 150 points
        ("brand-001", "CW-1002", 75, "TXN-CW-003"),   # Ayşe: 75 points
        ("brand-001", "CW-1003", 200, "TXN-CW-004"),  # Mehmet: 200 points

        # BookStore transactions
        ("brand-002", "BS-2001", 150, "TXN-BS-001"),  # Ahmet: 150 points
        ("brand-002", "BS-2002", 300, "TXN-BS-002"),  # Ayşe: 300 points
        ("brand-002", "BS-2003", 50, "TXN-BS-003"),   # Fatma: 50 points

        # FitLife transactions
        ("brand-003", "FL-3001", 500, "TXN-FL-001"),  # Ahmet: 500 points
        ("brand-003", "FL-3002", 250, "TXN-FL-002"),  # Can: 250 points
    ]

    # Track balances
    balances = {}

    for brand_id, customer_id, points, txn_id in transactions:
        # Create transaction
        composite_id = f"{brand_id}:{txn_id}"
        txn = Transaction(
            id=composite_id,
            txn_id=txn_id,
            brand_id=brand_id,
            user_id=customer_id,
            points=points
        )
        db.add(txn)

        # Update balance tracking
        balance_key = f"{brand_id}:{customer_id}"
        if balance_key not in balances:
            balances[balance_key] = 0
        balances[balance_key] += points

    db.commit()
    print(f"✓ Created {len(transactions)} transactions")

    # Create balance records
    for balance_key, points in balances.items():
        brand_id, customer_id = balance_key.split(":", 1)
        balance = Balance(
            brand_id=brand_id,
            user_id=customer_id,
            points=points
        )
        db.add(balance)

    db.commit()
    print(f"✓ Created {len(balances)} balance records")


def seed_provisions(db, brands):
    """Create test provisions for redemption scenarios"""
    print("\nSeeding provisions...")

    now = datetime.now(timezone.utc)

    provisions = [
        # Active provision for Ahmet in Coffee World (50 points, 30 mins)
        Provision(
            provision_id="PROV-CW-001",
            brand_id="brand-001",
            user_id="CW-1001",
            points=50,
            remaining_points=50,
            expires_at=now + timedelta(minutes=30)
        ),

        # Active provision for Ayşe in BookStore (100 points, 1 hour)
        Provision(
            provision_id="PROV-BS-001",
            brand_id="brand-002",
            user_id="BS-2002",
            points=100,
            remaining_points=100,
            expires_at=now + timedelta(hours=1)
        ),

        # Partially used provision for Ahmet in FitLife (200 points, 120 remaining, 2 hours)
        Provision(
            provision_id="PROV-FL-001",
            brand_id="brand-003",
            user_id="FL-3001",
            points=200,
            remaining_points=120,
            expires_at=now + timedelta(hours=2)
        ),

        # Expired provision for testing (should fail redemption)
        Provision(
            provision_id="PROV-CW-002",
            brand_id="brand-001",
            user_id="CW-1002",
            points=25,
            remaining_points=25,
            expires_at=now - timedelta(minutes=5)  # Expired 5 minutes ago
        ),
    ]

    for prov in provisions:
        db.add(prov)

    db.commit()
    print(f"✓ Created {len(provisions)} provisions")

    # Update balances to reflect locked points
    print("✓ Updating balances to reflect provisioned (locked) points...")

    # Deduct provisioned points from balances
    locked_points = [
        ("brand-001", "CW-1001", 50),   # Ahmet Coffee World: 150 - 50 = 100 available
        ("brand-002", "BS-2002", 100),  # Ayşe BookStore: 300 - 100 = 200 available
        ("brand-003", "FL-3001", 200),  # Ahmet FitLife: 500 - 200 = 300 available
        ("brand-001", "CW-1002", 25),   # Ayşe Coffee World: 75 - 25 = 50 available
    ]

    for brand_id, user_id, locked in locked_points:
        balance = db.query(Balance).filter(
            Balance.brand_id == brand_id,
            Balance.user_id == user_id
        ).first()
        if balance:
            balance.points -= locked

    db.commit()


def print_summary():
    """Print summary of seeded data"""
    print("\n" + "="*80)
    print("DATABASE SEEDED SUCCESSFULLY")
    print("="*80)

    print("\n📦 BRANDS:")
    print("  - brand-001: Coffee World")
    print("  - brand-002: BookStore Plus")
    print("  - brand-003: FitLife Gym")

    print("\n👥 CUSTOMERS:")
    print("  Phone: 5551234567 (Ahmet) - Member of ALL brands")
    print("    ├─ Coffee World: CW-1001 (100 available, 50 locked)")
    print("    ├─ BookStore: BS-2001 (150 points)")
    print("    └─ FitLife: FL-3001 (300 available, 200 locked, 120 remaining in provision)")
    print("\n  Phone: 5559876543 (Ayşe) - Member of Coffee World & BookStore")
    print("    ├─ Coffee World: CW-1002 (50 available, 25 locked EXPIRED)")
    print("    └─ BookStore: BS-2002 (200 available, 100 locked)")
    print("\n  Phone: 5555554444 (Mehmet) - Coffee World only")
    print("    └─ Coffee World: CW-1003 (200 points)")
    print("\n  Phone: 5552223333 (Fatma) - BookStore only")
    print("    └─ BookStore: BS-2003 (50 points)")
    print("\n  Phone: 5557778888 (Can) - FitLife only")
    print("    └─ FitLife: FL-3002 (250 points)")

    print("\n🎫 ACTIVE PROVISIONS:")
    print("  - PROV-CW-001: 50 points for CW-1001 (expires in 30 min)")
    print("  - PROV-BS-001: 100 points for BS-2002 (expires in 1 hour)")
    print("  - PROV-FL-001: 120/200 remaining for FL-3001 (expires in 2 hours)")
    print("  - PROV-CW-002: 25 points for CW-1002 (EXPIRED - for testing)")

    print("\n🧪 TEST SCENARIOS:")
    print("\n  1. Check if phone is registered:")
    print("     GET /brands/brand-001/customers/CW-1001")
    print("     → Should return customer with balance")

    print("\n  2. Check points balance:")
    print("     GET /brands/brand-001/customers/CW-1001/balance")
    print("     → Should return 100 points (150 earned - 50 locked)")

    print("\n  3. Create provision (locks points):")
    print("     POST /brands/brand-001/provision")
    print("     {\"customerId\": \"CW-1003\", \"points\": 50, \"provisionId\": \"PROV-TEST-001\", \"expiresAt\": \"...\"}")
    print("     → Should lock 50 points from Mehmet's 200")

    print("\n  4. Redeem with existing provision:")
    print("     POST /brands/brand-001/redeem")
    print("     {\"customerId\": \"CW-1001\", \"points\": 30, \"txnId\": \"TXN-REDEEM-001\", \"provisionId\": \"PROV-CW-001\"}")
    print("     → Should redeem 30 of 50 provisioned points")

    print("\n  5. Redeem partial amount:")
    print("     POST /brands/brand-003/redeem")
    print("     {\"customerId\": \"FL-3001\", \"points\": 50, \"txnId\": \"TXN-REDEEM-002\", \"provisionId\": \"PROV-FL-001\"}")
    print("     → Should redeem 50 of 120 remaining (70 will remain)")

    print("\n  6. Test expired provision:")
    print("     POST /brands/brand-001/redeem")
    print("     {\"customerId\": \"CW-1002\", \"points\": 25, \"txnId\": \"TXN-REDEEM-003\", \"provisionId\": \"PROV-CW-002\"}")
    print("     → Should fail with 410 Gone (expired)")

    print("\n  7. Test duplicate transaction ID:")
    print("     POST /brands/brand-001/earn")
    print("     {\"customerId\": \"CW-1001\", \"points\": 50, \"txnId\": \"TXN-CW-001\"}")
    print("     → Should fail with 409 Conflict (already exists)")

    print("\n  8. Test cross-brand transaction ID (should work):")
    print("     POST /brands/brand-002/earn")
    print("     {\"customerId\": \"BS-2001\", \"points\": 50, \"txnId\": \"TXN-CW-001\"}")
    print("     → Should succeed (same txnId but different brand)")

    print("\n" + "="*80)
    print("Server is running at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("="*80 + "\n")


def main():
    """Main seeding function"""
    print("\n" + "="*80)
    print("SEEDING DATABASE WITH TEST DATA")
    print("="*80)

    db = SessionLocal()
    try:
        clear_database()
        brands = seed_brands(db)
        brand_customers = seed_customers(db, brands)
        seed_transactions_and_balances(db, brands, brand_customers)
        seed_provisions(db, brands)
        print_summary()

    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
