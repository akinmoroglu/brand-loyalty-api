# Setup Guide

## Quick Start

Follow these steps to get the Brand Loyalty API running on your machine.

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git (optional, for cloning)

### Installation Steps

#### 1. Clone or Download the Repository

```bash
# If using git
git clone <repository-url>
cd 4-Loyalty

# Or download and extract the zip file
```

#### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Run the Application

```bash
# Option 1: Using uvicorn directly (recommended for development)
uvicorn main:app --reload

# Option 2: Using Python
python main.py
```

#### 5. Verify Installation

Open your browser and visit:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

You should see the API documentation with all endpoints.

## First API Call

Test the API is working:

```bash
# List all brands
curl http://localhost:8000/brands

# Expected response:
# [
#   {"id": "brand-001", "name": "Kahve Dünyası"},
#   {"id": "brand-002", "name": "Starbucks"},
#   ...
# ]
```

## Project Structure

After setup, your directory should look like this:

```
4-Loyalty/
├── app/                        # Application code
│   ├── api/                    # API routes
│   ├── core/                   # Business logic
│   ├── db/                     # Database config
│   ├── models/                 # Database models
│   └── schemas/                # Request/response schemas
├── venv/                       # Virtual environment (gitignored)
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── README.md                   # Main documentation
├── CUSTOMER_API.md            # Customer API details
├── MIGRATION_GUIDE.md         # Migration information
└── SETUP.md                   # This file
```

## Configuration

### Environment Variables (Optional)

Create a `.env` file in the root directory to override defaults:

```env
# Application
APP_NAME="My Loyalty API"
DEBUG=True

# Database
DATABASE_URL=sqlite:///./loyalty.db

# Security (not currently enforced)
API_KEY=your-secret-key
API_KEY_ENABLED=False
```

### Database

The application uses SQLite by default, which requires no additional setup. The database file (`loyalty.db`) will be created automatically on first run.

To use a different database, update `DATABASE_URL` in `app/core/config.py` or via environment variable.

## Development

### Running Tests

```bash
# Install test dependencies first
pip install pytest pytest-cov

# Run tests (when available)
pytest
```

### Auto-reload

Use `--reload` flag for automatic reloading during development:

```bash
uvicorn main:app --reload
```

The server will automatically restart when you modify any Python file.

### API Documentation

While the server is running, interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

You can test all endpoints directly from the Swagger UI.

## Common Issues

### Port Already in Use

If port 8000 is already in use:

```bash
# Option 1: Use a different port
uvicorn main:app --port 8001

# Option 2: Kill the process using port 8000
# On macOS/Linux:
lsof -ti:8000 | xargs kill -9

# On Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Module Not Found Error

If you see `ModuleNotFoundError`:

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Database Locked Error

If you get "database is locked" error:

```bash
# Stop the server
# Delete the database file
rm loyalty.db

# Restart the server (database will be recreated)
uvicorn main:app --reload
```

## Production Deployment

### Using Gunicorn (Linux/macOS)

```bash
# Install gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Using Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t loyalty-api .
docker run -p 8000:8000 loyalty-api
```

### Environment Considerations

For production:
1. Switch to PostgreSQL or MySQL instead of SQLite
2. Enable API key authentication
3. Use a reverse proxy (nginx)
4. Enable HTTPS
5. Set up proper logging
6. Use environment variables for sensitive data

## Next Steps

1. Read the [README.md](README.md) for API overview
2. Check [CUSTOMER_API.md](CUSTOMER_API.md) for customer management details
3. Review [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) if migrating from old code
4. Start making API calls and build your integration!

## Support

For issues or questions:
1. Check the documentation files in this repository
2. Review the interactive API docs at `/docs`
3. Examine the code in the `app/` directory

## Requirements

The application requires these Python packages:

```
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
sqlalchemy>=2.0.0
```

All requirements are listed in `requirements.txt`.
