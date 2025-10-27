# Customer Management API

## Overview

The loyalty system now includes comprehensive customer management where:
- Customers are identified by their **10-digit Turkish phone number**
- Each brand can assign their own **custom customer ID** to customers
- One customer (phone number) can be registered with **multiple brands**
- Each brand has their own unique customer ID for the same customer

## Customer Model

### Customer
- **Primary Key**: 10-digit Turkish phone number
- **Validation**: Must be exactly 10 digits
- **Global**: Same across all brands

### Brand-Customer Relationship
- **Brand ID**: The brand identifier
- **Phone Number**: Customer's phone number
- **Brand Customer ID**: Brand's custom ID for this customer
- **Many-to-Many**: One customer can belong to many brands, one brand can have many customers

## Example

Same customer with phone `5551234567` registered to two brands:

```
Brand: Kahve Dünyası (brand-001)
├─ Customer ID: KD-12345
├─ Phone: 5551234567
└─ Points: 100

Brand: Starbucks (brand-002)
├─ Customer ID: SB-ABCD
├─ Phone: 5551234567  (same person!)
└─ Points: 0
```

## API Endpoints

### 1. Register Customer to Brand

**POST** `/brands/{brand_id}/customers`

Register a customer to a brand with a brand-specific customer ID.

**Request Body:**
```json
{
  "phoneNumber": "5551234567",
  "brandCustomerId": "KD-12345"
}
```

**Response (201):**
```json
{
  "phoneNumber": "5551234567",
  "brandCustomerId": "KD-12345",
  "points": 0,
  "createdAt": "2025-10-27T15:44:57.540022"
}
```

**Error Cases:**
- `409`: Customer already registered with this brand
- `409`: Brand customer ID already exists for this brand

### 2. List All Customers of a Brand

**GET** `/brands/{brand_id}/customers`

Get all customers registered to a specific brand with their details.

**Response (200):**
```json
[
  {
    "phoneNumber": "5551234567",
    "brandCustomerId": "KD-12345",
    "points": 100,
    "createdAt": "2025-10-27T15:44:57.540022"
  },
  {
    "phoneNumber": "5559876543",
    "brandCustomerId": "KD-99999",
    "points": 50,
    "createdAt": "2025-10-27T15:45:02.988833"
  }
]
```

### 3. Get Customer Details

**GET** `/brands/{brand_id}/customers/{customer_id}`

Get specific customer details using the brand's customer ID.

**Response (200):**
```json
{
  "phoneNumber": "5551234567",
  "brandCustomerId": "KD-12345",
  "points": 100,
  "createdAt": "2025-10-27T15:44:57.540022"
}
```

**Error Cases:**
- `404`: Customer not found for this brand

### 4. Check Customer Balance

**GET** `/brands/{brand_id}/customers/{customer_id}/balance`

Get balance using the brand's customer ID.

**Response (200):**
```json
{
  "brandId": "brand-001",
  "customerId": "KD-12345",
  "phoneNumber": "5551234567",
  "points": 100,
  "updatedAt": "2025-10-27T15:45:13.295660"
}
```

**Error Cases:**
- `404`: Customer not found for this brand

## Updated Transaction Endpoints

All transaction endpoints now use **brand customer IDs** instead of generic user IDs:

### Earn Points

**POST** `/brands/{brand_id}/earn`

**Request Body:**
```json
{
  "customerId": "KD-12345",
  "points": 100,
  "txnId": "txn-001"
}
```

**Response:**
```json
{
  "status": "earned",
  "txnId": "txn-001",
  "brandId": "brand-001",
  "customerId": "KD-12345",
  "phoneNumber": "5551234567",
  "points": 100,
  "updatedAt": "2025-10-27T15:45:13.295660"
}
```

### Create Provision

**POST** `/brands/{brand_id}/provision`

**Request Body:**
```json
{
  "customerId": "KD-12345",
  "points": 50,
  "provisionId": "prov-001",
  "expiresAt": "2025-12-31T23:59:59Z"
}
```

### Redeem Points

**POST** `/brands/{brand_id}/redeem`

**Request Body:**
```json
{
  "customerId": "KD-12345",
  "points": 50,
  "txnId": "txn-002",
  "provisionId": "prov-001"
}
```

## Phone Number Validation

All phone numbers must:
- Be exactly **10 digits**
- Contain only numeric characters
- Match Turkish phone number format

Examples:
- ✅ `5551234567`
- ❌ `555-123-4567` (contains dashes)
- ❌ `+905551234567` (contains country code)
- ❌ `555123456` (too short)

## Database Schema

### customers table
```sql
phone_number VARCHAR(10) PRIMARY KEY
created_at DATETIME
```

### brand_customers table
```sql
id VARCHAR PRIMARY KEY  -- composite: "brand_id:phone_number"
brand_id VARCHAR (FK -> brands.id)
phone_number VARCHAR(10) (FK -> customers.phone_number)
brand_customer_id VARCHAR (brand's custom ID)
created_at DATETIME

UNIQUE INDEX: (brand_id, brand_customer_id)
UNIQUE INDEX: (brand_id, phone_number)
```

## Use Cases

### 1. Register New Customer
```bash
curl -X POST http://localhost:8000/brands/brand-001/customers \
  -H "Content-Type: application/json" \
  -d '{
    "phoneNumber": "5551234567",
    "brandCustomerId": "LOYALTY-2024-001"
  }'
```

### 2. Multi-Brand Customer
```bash
# Register to Brand A
curl -X POST http://localhost:8000/brands/brand-001/customers \
  -d '{"phoneNumber": "5551234567", "brandCustomerId": "BRAND-A-123"}'

# Same phone, register to Brand B
curl -X POST http://localhost:8000/brands/brand-002/customers \
  -d '{"phoneNumber": "5551234567", "brandCustomerId": "BRAND-B-XYZ"}'
```

### 3. List Brand's Customers
```bash
curl http://localhost:8000/brands/brand-001/customers
```

### 4. Earn Points for Customer
```bash
curl -X POST http://localhost:8000/brands/brand-001/earn \
  -H "Content-Type: application/json" \
  -d '{
    "customerId": "LOYALTY-2024-001",
    "points": 100,
    "txnId": "purchase-789"
  }'
```

## Benefits

1. **Privacy**: Phone numbers are internal, brands use their own IDs
2. **Flexibility**: Each brand can use their existing customer ID system
3. **Multi-Brand**: Customers can participate in multiple loyalty programs
4. **Consistency**: Same customer (phone) across brands with different IDs
5. **Validation**: Turkish phone number format enforced

## Migration Notes

### Breaking Changes

❌ **Old API** (deprecated):
```json
{
  "userId": "user123"
}
```

✅ **New API**:
```json
{
  "customerId": "BRAND-123"
}
```

### Steps to Migrate

1. Register all existing users as customers
2. Update all API calls to use `customerId` instead of `userId`
3. Update balance endpoint path: `/brands/{id}/users/{id}/balance` → `/brands/{id}/customers/{id}/balance`
