# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install packages
pip install -r requirements.txt
```

### 2. Run the Application

```bash
uvicorn main:app --reload
```

### 3. Open Your Browser

Visit: **http://localhost:8000/docs**

You'll see the interactive API documentation!

## 🎯 Try Your First API Calls

### List Brands

```bash
curl http://localhost:8000/brands
```

### Register a Customer

```bash
curl -X POST http://localhost:8000/brands/brand-001/customers \
  -H "Content-Type: application/json" \
  -d '{"phoneNumber":"5551234567","brandCustomerId":"CUST-001"}'
```

### Earn Points

```bash
curl -X POST http://localhost:8000/brands/brand-001/earn \
  -H "Content-Type: application/json" \
  -d '{"customerId":"CUST-001","points":100,"txnId":"txn-001"}'
```

### Check Balance

```bash
curl http://localhost:8000/brands/brand-001/customers/CUST-001/balance
```

## 📚 Documentation

- **[README.md](README.md)** - Full project overview
- **[SETUP.md](SETUP.md)** - Detailed setup instructions
- **[CUSTOMER_API.md](CUSTOMER_API.md)** - Customer management details
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Code organization
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Migration from old code

## 🔥 Key Features

✅ **Customer Management**: Register customers with brand-specific IDs
✅ **Multi-Brand Support**: Same customer, different IDs per brand
✅ **Phone Validation**: 10-digit Turkish phone number format
✅ **Point Transactions**: Earn, redeem, and void points
✅ **Provisions**: Temporary point reservations with expiry
✅ **Clean Architecture**: Easy to maintain and extend

## 📖 API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/brands` | GET | List all brands |
| `/brands/{id}/customers` | POST | Register customer |
| `/brands/{id}/customers` | GET | List customers |
| `/brands/{id}/customers/{cid}/balance` | GET | Check balance |
| `/brands/{id}/earn` | POST | Earn points |
| `/brands/{id}/redeem` | POST | Redeem points |
| `/brands/{id}/provision` | POST | Create provision |

## 💡 Project Structure

```
4-Loyalty/
├── app/                    # Application code
│   ├── api/               # API endpoints
│   ├── core/              # Business logic
│   ├── db/                # Database config
│   ├── models/            # Database models
│   └── schemas/           # Request/response schemas
├── main.py                # Entry point
├── requirements.txt       # Dependencies
└── *.md                   # Documentation
```

## 🐛 Troubleshooting

### Port Already in Use?

```bash
uvicorn main:app --port 8001
```

### Module Not Found?

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Need Fresh Database?

```bash
rm loyalty.db
uvicorn main:app --reload
```

## 🎓 Example Workflow

```bash
# 1. Register a customer
curl -X POST http://localhost:8000/brands/brand-001/customers \
  -H "Content-Type: application/json" \
  -d '{"phoneNumber":"5551234567","brandCustomerId":"KD-12345"}'

# 2. Earn points (purchase)
curl -X POST http://localhost:8000/brands/brand-001/earn \
  -H "Content-Type: application/json" \
  -d '{"customerId":"KD-12345","points":100,"txnId":"txn-001"}'

# 3. Check balance
curl http://localhost:8000/brands/brand-001/customers/KD-12345/balance

# 4. Create provision (reserve points)
curl -X POST http://localhost:8000/brands/brand-001/provision \
  -H "Content-Type: application/json" \
  -d '{
    "customerId":"KD-12345",
    "points":50,
    "provisionId":"prov-001",
    "expiresAt":"2025-12-31T23:59:59Z"
  }'

# 5. Redeem points
curl -X POST http://localhost:8000/brands/brand-001/redeem \
  -H "Content-Type: application/json" \
  -d '{
    "customerId":"KD-12345",
    "points":50,
    "txnId":"txn-002",
    "provisionId":"prov-001"
  }'
```

## 🌟 What Makes This Special?

1. **Multi-Brand Architecture**: One customer can participate in multiple loyalty programs
2. **Brand-Specific IDs**: Each brand uses their own customer identification system
3. **Turkish Phone Support**: Validates 10-digit Turkish phone numbers
4. **Clean Code**: Professional structure following FastAPI best practices
5. **Ready to Share**: Fully documented and production-ready

## 🔗 Next Steps

1. ✅ Run the application
2. ✅ Try the API calls above
3. ✅ Explore `/docs` for interactive testing
4. ✅ Read the detailed documentation
5. ✅ Build your integration!

## 📞 Need Help?

- Check the **[SETUP.md](SETUP.md)** for detailed instructions
- Review the **[CUSTOMER_API.md](CUSTOMER_API.md)** for API details
- Explore the interactive docs at **/docs** when the server is running

---

**Ready to go? Start with step 1 above! 🚀**
