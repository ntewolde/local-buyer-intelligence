# Quick Start Guide

Get the Local Buyer Intelligence Platform running in 5 minutes.

## Prerequisites

- Docker and Docker Compose installed
- OR Python 3.9+, Node.js 18+, PostgreSQL, Redis

## Option 1: Docker (Recommended)

```bash
# 1. Navigate to project
cd local-buyer-intelligence

# 2. Create backend .env file
cat > backend/.env << EOF
DATABASE_URL=postgresql://local_buyer:local_buyer_password@postgres:5432/local_buyer_intelligence
REDIS_URL=redis://redis:6379/0
SECRET_KEY=dev-secret-key-change-in-production
MAPBOX_ACCESS_TOKEN=your_token_here
ENVIRONMENT=development
EOF

# 3. Start services
docker-compose up -d

# 4. Run migrations
docker-compose exec backend alembic upgrade head

# 5. Check API is running
curl http://localhost:8000/health

# 6. Open API docs
# Visit http://localhost:8000/docs in your browser
```

**Backend API**: http://localhost:8000  
**API Docs**: http://localhost:8000/docs

## Option 2: Manual Setup

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (see backend/.env.example)
# Set DATABASE_URL, REDIS_URL, SECRET_KEY, etc.

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

**Backend**: http://localhost:8000  
**Frontend**: http://localhost:3000

## First Steps

### 1. Create a Geography

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

Save the `id` from the response.

### 2. Create a ZIP Code

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

### 3. Create Sample Household Data

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
    "income_band_max": 80000,
    "property_age_years": 15
  }'
```

### 4. Generate an Intelligence Report

```bash
curl -X POST "http://localhost:8000/api/v1/intelligence/reports" \
  -H "Content-Type: application/json" \
  -d '{
    "geography_id": 1,
    "zip_codes": "10001",
    "service_category": "lawn_care",
    "report_name": "My First Report"
  }'
```

### 5. View the Report

The response will include:
- Total households
- Target households
- Average demand score
- Buyer profile (property types, income distribution, etc.)
- ZIP code demand scores
- Channel recommendations
- Timing recommendations

## Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs for interactive API documentation
2. **Add More Data**: Create more geographies, ZIP codes, and household records
3. **Run Data Collectors**: Implement and run data collectors to populate real data
4. **Generate Reports**: Experiment with different service categories and geographies
5. **Customize Scoring**: Adjust demand scoring algorithms in `app/services/intelligence_engine.py`

## Troubleshooting

### Database Connection Error

- Check PostgreSQL is running: `docker-compose ps postgres`
- Verify DATABASE_URL in `.env` file
- Check database exists: `docker-compose exec postgres psql -U local_buyer -l`

### Redis Connection Error

- Check Redis is running: `docker-compose ps redis`
- Test connection: `docker-compose exec redis redis-cli ping`

### Migration Errors

- Reset database: `docker-compose down -v && docker-compose up -d`
- Re-run migrations: `docker-compose exec backend alembic upgrade head`

### Port Already in Use

- Change ports in `docker-compose.yml`
- Or stop services using those ports

## Resources

- **Full Setup Guide**: See [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Implementation Notes**: See [IMPLEMENTATION_NOTES.md](IMPLEMENTATION_NOTES.md)
- **Main README**: See [README.md](README.md)

