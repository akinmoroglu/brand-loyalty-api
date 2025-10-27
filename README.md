# Brand Loyalty API

A well-structured FastAPI application for managing brand loyalty programs with points tracking, provisioning, and redemption.

## Project Structure

```
4-Loyalty/
├── app/
│   ├── __init__.py
│   ├── api/                    # API route handlers
│   │   ├── __init__.py
│   │   ├── brands.py           # Brand management endpoints
│   │   ├── balances.py         # Balance checking endpoints
│   │   ├── transactions.py     # Earn/redeem/void endpoints
│   │   └── provisions.py       # Provision management endpoints
│   ├── core/                   # Core business logic
│   │   ├── __init__.py
│   │   ├── config.py           # Application settings
│   │   └── crud.py             # Database operations
│   ├── db/                     # Database configuration
│   │   ├── __init__.py
│   │   ├── base.py             # SQLAlchemy base
│   │   ├── session.py          # Database session management
│   │   └── init_db.py          # Database initialization
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── brand.py
│   │   ├── balance.py
│   │   ├── transaction.py
│   │   └── provision.py
│   └── schemas/                # Pydantic schemas
│       ├── __init__.py
│       ├── brand.py
│       ├── balance.py
│       ├── transaction.py
│       └── provision.py
├── main.py                     # Application entry point
├── requirements.txt
└── README.md
```

## Features

- **Brand Management**: Create and list brands
- **Balance Tracking**: Track user points per brand
- **Earn Points**: Add points to user accounts
- **Provisions**: Reserve points for later redemption with expiry
- **Redeem Points**: Spend points using provisions
- **Void Transactions**: Reverse previous transactions
- **SQLite Database**: Persistent storage with proper migrations
- **Clean Architecture**: Separation of concerns with proper layering

## Installation

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

```bash
# Development mode with auto-reload
uvicorn main:app --reload

# Or use the Python script
python main.py
```

The API will be available at: `http://localhost:8000`

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Brands
- `GET /brands` - List all brands
- `POST /brands` - Create a new brand
- `GET /brands/{brand_id}` - Get specific brand

### Customers ✨ NEW
- `POST /brands/{brand_id}/customers` - Register a customer to a brand
- `GET /brands/{brand_id}/customers` - List all customers of a brand
- `GET /brands/{brand_id}/customers/{customer_id}` - Get customer details
- `GET /brands/{brand_id}/customers/{customer_id}/balance` - Get customer balance

### Transactions
- `POST /brands/{brand_id}/earn` - Earn points (uses customerId)
- `POST /brands/{brand_id}/redeem` - Redeem points (uses customerId)
- `POST /brands/{brand_id}/void` - Void a transaction

### Provisions
- `POST /brands/{brand_id}/provision` - Create a provision (uses customerId)
- `GET /provisions/{provision_id}` - Check provision status

📖 **Detailed Customer API Documentation**: See [CUSTOMER_API.md](CUSTOMER_API.md)

## Configuration

Edit `app/core/config.py` to customize:
- Database URL
- API settings
- Authentication (currently disabled)

## Architecture Benefits

### 1. **Separation of Concerns**
- Models: Database structure
- Schemas: API input/output validation
- CRUD: Database operations
- API: HTTP request handling

### 2. **Maintainability**
- Easy to locate and modify specific functionality
- Clear dependencies between modules
- Testable components

### 3. **Scalability**
- Easy to add new endpoints
- Simple to switch databases
- Can add middleware, authentication, etc.

### 4. **Best Practices**
- Type hints throughout
- Pydantic validation
- Dependency injection
- Proper error handling
- RESTful API design

## Example Usage

### Create a Brand
```bash
curl -X POST http://localhost:8000/brands \
  -H "Content-Type: application/json" \
  -d '{"id": "brand-007", "name": "Costa Coffee"}'
```

### Earn Points
```bash
curl -X POST http://localhost:8000/brands/brand-001/earn \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user123",
    "points": 100,
    "txnId": "txn-001"
  }'
```

### Check Balance
```bash
curl http://localhost:8000/brands/brand-001/users/user123/balance
```

## Development

To add new features:

1. Add database model in `app/models/`
2. Create Pydantic schema in `app/schemas/`
3. Add CRUD operations in `app/core/crud.py`
4. Create API routes in `app/api/`
5. Register routes in `app/api/__init__.py`

## Turkish Character Support

The application fully supports Turkish characters (ğ, ü, ş, ı, ö, ç) in brand names and all text fields.

## Migration from Old Code

The old monolithic file `mock_brand_db.py` has been refactored into a proper project structure. All functionality remains the same, but the code is now:
- More organized
- Easier to maintain
- Better documented
- More testable
- Follows FastAPI best practices
