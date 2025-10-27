# Project Structure

## Overview

This document describes the complete structure of the Brand Loyalty API project.

## Directory Tree

```
4-Loyalty/
├── app/                                    # Main application package
│   ├── __init__.py
│   │
│   ├── api/                                # API route handlers
│   │   ├── __init__.py                     # Router registration
│   │   ├── balances.py                     # Balance checking endpoints
│   │   ├── brands.py                       # Brand management endpoints
│   │   ├── customers.py                    # Customer management endpoints ✨
│   │   ├── provisions.py                   # Provision management endpoints
│   │   └── transactions.py                 # Transaction endpoints (earn/redeem/void)
│   │
│   ├── core/                               # Business logic & configuration
│   │   ├── __init__.py
│   │   ├── config.py                       # Application settings
│   │   └── crud.py                         # Database CRUD operations
│   │
│   ├── db/                                 # Database configuration
│   │   ├── __init__.py
│   │   ├── base.py                         # SQLAlchemy base class
│   │   ├── init_db.py                      # Database initialization
│   │   └── session.py                      # Database session management
│   │
│   ├── models/                             # SQLAlchemy database models
│   │   ├── __init__.py
│   │   ├── balance.py                      # Balance model
│   │   ├── brand.py                        # Brand model
│   │   ├── brand_customer.py               # Brand-Customer relationship ✨
│   │   ├── customer.py                     # Customer model ✨
│   │   ├── provision.py                    # Provision model
│   │   └── transaction.py                  # Transaction model
│   │
│   └── schemas/                            # Pydantic request/response schemas
│       ├── __init__.py
│       ├── balance.py                      # Balance schemas
│       ├── brand.py                        # Brand schemas
│       ├── customer.py                     # Customer schemas ✨
│       ├── provision.py                    # Provision schemas
│       └── transaction.py                  # Transaction schemas
│
├── venv/                                   # Virtual environment (gitignored)
│
├── .gitignore                              # Git ignore rules
├── CUSTOMER_API.md                         # Customer API documentation ✨
├── MIGRATION_GUIDE.md                      # Migration from old code
├── PROJECT_STRUCTURE.md                    # This file
├── README.md                               # Main documentation
├── SETUP.md                                # Setup instructions
├── main.py                                 # Application entry point
├── requirements.txt                        # Python dependencies
├── MockBrandLoyalty.postman_collection.json # Postman collection (legacy)
└── openapi.yaml                            # OpenAPI specification (legacy)
```

✨ = New files added for customer management feature

## File Descriptions

### Root Files

| File | Purpose |
|------|---------|
| `main.py` | FastAPI application entry point and startup configuration |
| `requirements.txt` | Python package dependencies |
| `README.md` | Main project documentation and overview |
| `SETUP.md` | Installation and setup instructions |
| `CUSTOMER_API.md` | Detailed customer management API documentation |
| `MIGRATION_GUIDE.md` | Guide for migrating from monolithic code |
| `PROJECT_STRUCTURE.md` | This file - project structure documentation |
| `.gitignore` | Files and directories to ignore in version control |

### Application Package (`app/`)

#### API Layer (`app/api/`)

Route handlers for different API domains:

- **`__init__.py`**: Registers all routers with the main API router
- **`brands.py`**: Brand CRUD operations (list, create, get)
- **`customers.py`**: Customer registration, listing, and details
- **`balances.py`**: Balance checking for customers
- **`transactions.py`**: Earn, redeem, and void point transactions
- **`provisions.py`**: Create and check point provisions

#### Core Layer (`app/core/`)

Business logic and configuration:

- **`config.py`**: Application settings and configuration
- **`crud.py`**: Database operations organized by entity (Brand, Customer, Transaction, etc.)

#### Database Layer (`app/db/`)

Database setup and management:

- **`base.py`**: SQLAlchemy declarative base
- **`session.py`**: Database session factory and dependency injection
- **`init_db.py`**: Initial data seeding (sample brands)

#### Models Layer (`app/models/`)

SQLAlchemy ORM models:

- **`brand.py`**: Brand entity (id, name)
- **`customer.py`**: Customer entity (phone_number)
- **`brand_customer.py`**: Many-to-many relationship (brand + customer + brand_customer_id)
- **`balance.py`**: Point balances per brand-customer
- **`transaction.py`**: Transaction history
- **`provision.py`**: Temporary point reservations

#### Schemas Layer (`app/schemas/`)

Pydantic models for request/response validation:

- **`brand.py`**: Brand request/response schemas
- **`customer.py`**: Customer and BrandCustomer schemas
- **`balance.py`**: Balance response schema
- **`transaction.py`**: Earn, redeem, void request schemas
- **`provision.py`**: Provision request/response schemas

## Architecture Patterns

### Layered Architecture

```
┌─────────────────────────────────────┐
│   API Layer (app/api/)              │  ← HTTP endpoints
│   - Route handlers                  │
│   - Request/response validation     │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│   Business Layer (app/core/)        │  ← Business logic
│   - CRUD operations                 │
│   - Data transformation             │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│   Data Layer (app/models/)          │  ← Data persistence
│   - Database models                 │
│   - Relationships                   │
└─────────────────────────────────────┘
```

### Separation of Concerns

1. **Routes** (`app/api/`) - Handle HTTP requests/responses
2. **Schemas** (`app/schemas/`) - Validate and serialize data
3. **CRUD** (`app/core/crud.py`) - Database operations
4. **Models** (`app/models/`) - Database structure
5. **Config** (`app/core/config.py`) - Settings management

## Key Design Decisions

### 1. Customer Management

- **Phone Number as Primary Key**: 10-digit Turkish phone number uniquely identifies customers globally
- **Brand-Specific IDs**: Each brand assigns their own customer ID via `BrandCustomer` model
- **Many-to-Many**: One customer can belong to multiple brands with different IDs

### 2. Database Design

- **SQLite Default**: Easy development, no external dependencies
- **Foreign Keys**: Proper relationships between entities
- **Unique Constraints**: Prevent duplicate registrations and customer IDs
- **Timestamps**: Track creation and update times

### 3. API Design

- **RESTful**: Standard HTTP methods and status codes
- **Resource-Based URLs**: `/brands/{id}/customers/{id}`
- **Consistent Responses**: All responses follow similar structure
- **Error Handling**: Proper HTTP status codes and error messages

### 4. Code Organization

- **Feature-Based**: Each domain has its own route file
- **Single Responsibility**: Each file has one clear purpose
- **Dependency Injection**: Database sessions injected via FastAPI
- **Type Safety**: Type hints throughout the codebase

## Database Schema

### Tables

1. **brands**: Brand information
2. **customers**: Customer information (phone numbers)
3. **brand_customers**: Brand-customer relationships with brand-specific IDs
4. **balances**: Point balances per brand-customer
5. **transactions**: Transaction history
6. **provisions**: Temporary point reservations

### Relationships

```
brands ──┬── brand_customers ──┬── customers
         │                     │
         └── balances ─────────┘
         │
         └── transactions
         │
         └── provisions
```

## File Count Summary

- **Total Files**: 35 (excluding venv and cache)
- **Python Files**: 24
- **Documentation**: 6 markdown files
- **Configuration**: 2 files (.gitignore, requirements.txt)
- **Legacy**: 2 files (openapi.yaml, postman collection)

## Lines of Code (Approximate)

- **API Routes**: ~400 lines
- **CRUD Operations**: ~170 lines
- **Models**: ~100 lines
- **Schemas**: ~150 lines
- **Configuration**: ~50 lines
- **Total Application Code**: ~870 lines

## Adding New Features

To add a new feature:

1. Create model in `app/models/new_feature.py`
2. Create schema in `app/schemas/new_feature.py`
3. Add CRUD operations in `app/core/crud.py`
4. Create routes in `app/api/new_feature.py`
5. Register router in `app/api/__init__.py`
6. Update documentation

## Testing Structure (Future)

```
tests/
├── test_api/               # API endpoint tests
├── test_crud/              # CRUD operation tests
├── test_models/            # Model tests
└── conftest.py             # Pytest configuration
```

## Deployment Structure (Future)

```
4-Loyalty/
├── docker/                 # Docker configurations
├── scripts/                # Deployment scripts
├── tests/                  # Test suite
└── docs/                   # Additional documentation
```

## Version History

- **v1.0.0**: Initial refactored version with clean architecture
- **v1.1.0**: Added customer management with multi-brand support
