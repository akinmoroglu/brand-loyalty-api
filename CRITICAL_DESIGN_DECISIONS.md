# Critical Design Decisions

## 1. Transaction ID Management 🔴 CRITICAL

### Question
How is transaction ID managed among different brands and customers?

### Answer: **Transaction IDs are Scoped Per Brand**

#### ✅ **Fixed Implementation:**

Transaction IDs are **unique per brand**, NOT globally unique across all brands.

**What this means:**
- Brand A can use `txn-001`
- Brand B can also use `txn-001` (different brand, no conflict)
- Same brand cannot reuse `txn-001` twice

#### Database Schema:

```sql
CREATE TABLE transactions (
    id VARCHAR PRIMARY KEY,           -- Composite: "brand-001:txn-001"
    txn_id VARCHAR NOT NULL,          -- Brand's transaction ID
    brand_id VARCHAR NOT NULL,        -- The brand
    user_id VARCHAR NOT NULL,         -- Customer's phone
    points INTEGER NOT NULL,
    created_at DATETIME,

    UNIQUE INDEX (brand_id, txn_id)   -- ✅ Unique per brand
);
```

#### Why This Design?

**Scenario:**
- **Brand A** (Starbucks) uses POS system that generates: `POS-001`, `POS-002`...
- **Brand B** (Kahve Dünyası) also uses POS system that generates: `POS-001`, `POS-002`...

Both brands should be able to use their own transaction IDs without conflicts!

#### Example:

```bash
# Brand A - Starbucks
POST /brands/brand-002/earn
{
  "customerId": "SB-123",
  "points": 50,
  "txnId": "POS-001"  ✅ Works
}

# Brand B - Kahve Dünyası
POST /brands/brand-001/earn
{
  "customerId": "KD-456",
  "points": 100,
  "txnId": "POS-001"  ✅ Also works! (Different brand)
}

# Brand A - Starbucks again
POST /brands/brand-002/earn
{
  "customerId": "SB-789",
  "points": 75,
  "txnId": "POS-001"  ❌ FAILS - Already used for this brand!
}
```

#### Error Response:

```json
{
  "detail": "Transaction ID 'POS-001' already used for this brand"
}
```

#### Benefits:

1. ✅ **Brand Independence** - Each brand controls their own transaction IDs
2. ✅ **No Conflicts** - Brands don't interfere with each other
3. ✅ **Realistic** - Matches how real POS/payment systems work
4. ✅ **Scalable** - Can add unlimited brands without ID collisions

---

## 2. Provision ID Management 🔑

### Question
We assume that people who use the API are giving the provision ID, and the API keeps it right?

### Answer: **YES - Client Provides & Controls Provision IDs**

#### How It Works:

**Client Responsibility:**
- ✅ Client **generates** the provision ID
- ✅ Client **provides** it in the request
- ✅ Client must ensure it's unique (API will reject duplicates)

**API Responsibility:**
- ✅ Validates provision ID is unique (globally)
- ✅ Stores and tracks the provision
- ✅ Associates it with brand + customer + points
- ✅ Enforces expiry time
- ✅ Tracks partial redemptions

#### Why Client Generates?

**Use Case Example:**

```
Payment Gateway Flow:
1. Customer wants to redeem 100 points at checkout
2. Payment system generates: provision-uuid-12345
3. Calls API: POST /provision with this ID
4. Points are locked, provision created
5. If payment succeeds → Call /redeem with same provision ID
6. If payment fails → Provision expires automatically
```

This allows:
- **Idempotency** - Same provision ID can't be created twice
- **Tracking** - Payment system can track their own provision IDs
- **Recovery** - Can check provision status if connection drops

#### Provision ID Scope: **GLOBALLY UNIQUE**

Unlike transaction IDs (per-brand), provision IDs are globally unique across ALL brands.

**Why?**
- Provisions are temporary locks on points
- Need to prevent accidental reuse across brands
- Simpler for clients (don't need to track brand context)

#### Example:

```bash
# Brand A creates provision
POST /brands/brand-001/provision
{
  "customerId": "CUST-001",
  "points": 100,
  "provisionId": "prov-abc-123",  ✅ Created
  "expiresAt": "2025-12-31T23:59:59Z"
}

# Brand B tries same provision ID
POST /brands/brand-002/provision
{
  "customerId": "CUST-002",
  "points": 50,
  "provisionId": "prov-abc-123",  ❌ FAILS - Already exists!
  "expiresAt": "2025-12-31T23:59:59Z"
}
```

#### Error Response:

```json
{
  "detail": "Provision ID 'prov-abc-123' already exists"
}
```

#### Best Practices for Clients:

**Generate Unique Provision IDs:**

```javascript
// Good: UUID
provisionId = `prov-${brand}-${uuid.v4()}`
// Example: "prov-brand001-550e8400-e29b-41d4-a716"

// Good: Timestamp + Random
provisionId = `prov-${Date.now()}-${Math.random()}`
// Example: "prov-1698765432000-0.abc123"

// Bad: Sequential
provisionId = "prov-001"  // ❌ Will conflict across brands
```

---

## 3. ID Management Summary

| ID Type | Scope | Who Generates | Example | Uniqueness |
|---------|-------|---------------|---------|------------|
| **Transaction ID** | Per Brand | Client (POS/System) | `POS-001` | Unique per brand |
| **Provision ID** | Global | Client (Payment/App) | `prov-uuid-123` | Globally unique |
| **Customer ID** | Per Brand | Client/Brand | `CUST-001` | Unique per brand |
| **Phone Number** | Global | Customer | `5551234567` | Globally unique |

---

## 4. Complete Workflow Example

### Scenario: Customer Redeems Points at Checkout

```bash
# Step 1: Create Provision (Lock Points)
POST /brands/brand-001/provision
{
  "customerId": "CUST-001",
  "points": 100,
  "provisionId": "checkout-session-abc123",
  "expiresAt": "2025-10-27T19:00:00Z"  # 30 min from now
}

Response:
{
  "status": "provisioned",
  "provisionedPoints": 100,
  "remainingBalance": 50,  # Customer had 150, now 50 available
  ...
}

# Step 2a: Payment Succeeds - Redeem Points
POST /brands/brand-001/redeem
{
  "customerId": "CUST-001",
  "points": 100,
  "txnId": "payment-xyz789",  # From payment gateway
  "provisionId": "checkout-session-abc123"
}

Response:
{
  "status": "redeemed",
  "provisionStatus": "fully_redeemed",
  ...
}

# OR Step 2b: Payment Fails - Provision Expires
# After 30 minutes, provision expires automatically
# Points return to customer's available balance
```

---

## 5. Database Relationships

```
Brands (brand-001, brand-002, ...)
  ↓
Brand-Customers (brand + customer_id mapping)
  ↓
Transactions (brand:txn_id composite key)
  ↓
Balances (brand + phone_number)
  ↓
Provisions (global provision_id)
```

---

## 6. Key Takeaways

### ✅ Transaction IDs
- Scoped **per brand**
- Client generates based on their POS/system
- Same ID can exist for different brands

### ✅ Provision IDs
- Scoped **globally**
- Client generates (recommended: UUID)
- Must be unique across all brands
- Used for temporary point locks

### ✅ Why This Design?
- **Realistic**: Matches real-world multi-brand systems
- **Flexible**: Each brand uses their own ID schemes
- **Safe**: Prevents cross-brand conflicts
- **Scalable**: Works with unlimited brands

---

## 7. Testing the New Design

```bash
# Test: Same transaction ID, different brands
curl -X POST http://localhost:8000/brands/brand-001/earn \
  -d '{"customerId":"C1","points":100,"txnId":"TXN-001"}'
# ✅ Success

curl -X POST http://localhost:8000/brands/brand-002/earn \
  -d '{"customerId":"C2","points":50,"txnId":"TXN-001"}'
# ✅ Success (different brand)

curl -X POST http://localhost:8000/brands/brand-001/earn \
  -d '{"customerId":"C3","points":75,"txnId":"TXN-001"}'
# ❌ Fails: "Transaction ID 'TXN-001' already used for this brand"
```

---

**Server is running with the fixed implementation!**
Visit: http://localhost:8000/docs
