from sqlalchemy.orm import Session
from app.models import Brand


def init_brands(db: Session) -> None:
    """Initialize sample brands if database is empty"""
    if db.query(Brand).count() == 0:
        brands = [
            Brand(id="brand-001", name="Kahve Dünyası"),
            Brand(id="brand-002", name="Starbucks"),
            Brand(id="brand-003", name="Mado"),
            Brand(id="brand-004", name="Tchibo"),
            Brand(id="brand-005", name="Café Pierre"),
            Brand(id="brand-006", name="Café Nero")
        ]
        db.add_all(brands)
        db.commit()
        print("✓ Sample brands initialized")


def init_db(db: Session) -> None:
    """Initialize database with sample data"""
    init_brands(db)
