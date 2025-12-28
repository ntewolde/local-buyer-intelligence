# Setup Guide - Local Buyer Intelligence Platform

This guide will help you set up and run the Local Buyer Intelligence Platform.

## Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- PostgreSQL 14 or higher
- Redis (for Celery background tasks)
- Docker and Docker Compose (optional, for easy setup)

## Important: PII Compliance

This platform is designed to **never store or process PII (Personal Identifiable Information)**. All data collection, storage, and APIs are enforced to be PII-free. See the main README for details.

## Quick Start with Docker

The easiest way to get started is using Docker Compose:

```bash
# Clone or navigate to the project directory
cd local-buyer-intelligence

# Create .env file for backend (copy from .env.example template)
cp backend/.env.example backend/.env
# Edit backend/.env and update database credentials to match docker-compose.yml

# Start all services
docker-compose up -d

# Run database migrations
docker-compose exec backend alembic upgrade head

# Backend API will be available at http://localhost:8000
# Frontend will need to be started separately (see below)
```

## Manual Setup

### 1. Database Setup

```bash
# Create PostgreSQL database
createdb local_buyer_intelligence

# Or using psql
psql -U postgres
CREATE DATABASE local_buyer_intelligence;
\q
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
# Copy .env.example and update with your settings:
# - DATABASE_URL: postgresql://user:password@localhost:5432/local_buyer_intelligence
# - REDIS_URL: redis://localhost:6379/0
# - SECRET_KEY: generate a secure random key
# - MAPBOX_ACCESS_TOKEN: get from https://account.mapbox.com/

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

### 3. Celery Worker Setup

In a separate terminal:

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start Celery worker
celery -A app.core.celery_app worker --loglevel=info
```

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file (optional)
# NEXT_PUBLIC_API_URL=http://localhost:8000
# NEXT_PUBLIC_MAPBOX_TOKEN=your_mapbox_token_here

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Initial Setup (Create Admin User)

After running migrations, you must create the first client and admin user. See [QUICK_START.md](QUICK_START.md) for a Python script, or use this:

```python
# backend/create_admin.py
from app.core.database import SessionLocal
from app.models.client import Client, User, UserRole
from app.core.security import get_password_hash
import uuid

db = SessionLocal()

# Create client
client = Client(id=uuid.uuid4(), name="Default Client")
db.add(client)
db.commit()

# Create admin user
admin = User(
    id=uuid.uuid4(),
    client_id=client.id,
    email="admin@example.com",
    hashed_password=get_password_hash("changeme"),
    role=UserRole.ADMIN,
    is_active=True
)
db.add(admin)
db.commit()

print(f"Admin created: {admin.email} / changeme")
```

Run: `python create_admin.py`

## Initial Data Setup

After creating the admin user, you can start using the platform:

### 1. Create Geography Records

You can create geography records via the API:

```bash
curl -X POST "http://localhost:8000/api/v1/geography/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New York",
    "type": "city",
    "state_code": "NY",
    "latitude": 40.7128,
    "longitude": -74.0060
  }'
```

### 2. Create ZIP Code Records

```bash
curl -X POST "http://localhost:8000/api/v1/geography/zip-codes/" \
  -H "Content-Type: application/json" \
  -d '{
    "zip_code": "10001",
    "geography_id": 1,
    "latitude": 40.7505,
    "longitude": -73.9973,
    "population": 20000,
    "household_count": 8000,
    "median_income": 65000
  }'
```

### 3. Create Household Records

Household records should be created via data collectors. See the collectors documentation for more details.

You can also create test records via API:

```bash
curl -X POST "http://localhost:8000/api/v1/households/" \
  -H "Content-Type: application/json" \
  -d '{
    "zip_code_id": 1,
    "property_type": "single_family",
    "ownership_type": "owner",
    "property_sqft_min": 2000,
    "property_sqft_max": 2500,
    "lot_size_sqft": 8000,
    "income_band_min": 60000,
    "income_band_max": 80000
  }'
```

## Testing the API

Once everything is running, you can test the API:

```bash
# Health check (no auth required)
curl http://localhost:8000/health

# Login to get token
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=changeme" \
  | jq -r '.access_token')

# List geographies (requires auth)
curl http://localhost:8000/api/v1/geography/ \
  -H "Authorization: Bearer $TOKEN"

# Generate an intelligence report
curl -X POST "http://localhost:8000/api/v1/intelligence/reports" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "geography_id": 1,
    "zip_codes": "10001,10002",
    "service_category": "lawn_care",
    "report_name": "Test Report"
  }'
```

**Note**: Most API endpoints require authentication. Use the interactive docs at http://localhost:8000/docs - it has a "Authorize" button to enter your token.

## Development Workflow

### Running Tests

```bash
# Backend tests (when available)
cd backend
pytest

# Frontend tests (when available)
cd frontend
npm test
```

### Database Migrations

```bash
cd backend

# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Code Formatting

```bash
# Backend (install black and isort)
pip install black isort
black app/
isort app/

# Frontend
cd frontend
npm run lint
```

## Environment Variables

### Backend (.env)

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: Secret key for JWT tokens (generate a secure random string)
- `MAPBOX_ACCESS_TOKEN`: Mapbox API token for maps
- `ENVIRONMENT`: `development` or `production`
- `CORS_ORIGINS`: Comma-separated list of allowed origins

### Frontend (.env.local)

- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:8000)
- `NEXT_PUBLIC_MAPBOX_TOKEN`: Mapbox access token

## Troubleshooting

### Database Connection Issues

- Ensure PostgreSQL is running
- Check DATABASE_URL in .env file
- Verify database exists: `psql -l | grep local_buyer_intelligence`

### Redis Connection Issues

- Ensure Redis is running: `redis-cli ping` should return `PONG`
- Check REDIS_URL in .env file

### Migration Issues

- If migrations fail, you may need to drop and recreate the database
- Always backup data before running migrations in production

### Port Conflicts

- Backend defaults to port 8000
- Frontend defaults to port 3000
- PostgreSQL defaults to port 5432
- Redis defaults to port 6379

Change ports in docker-compose.yml or configuration files if needed.

## Next Steps

1. **Configure Data Collectors**: Set up API keys and endpoints for data sources
2. **Add Geography Data**: Import ZIP codes and geography data for your target areas
3. **Run Data Collection**: Execute collectors to populate household and demand signal data
4. **Generate Reports**: Use the API or frontend to generate intelligence reports
5. **Customize Scoring**: Adjust demand scoring algorithms in `intelligence_engine.py`

## Support

For issues or questions, refer to the main README.md or create an issue in the project repository.

