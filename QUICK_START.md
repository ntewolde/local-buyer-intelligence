# Quick Start Guide

Get the Local Buyer Intelligence Platform running in 5 minutes.

## Prerequisites

- Docker and Docker Compose installed
- OR Python 3.9+, Node.js 18+, PostgreSQL 14+, Redis

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

# 5. Create initial admin user (see Initial Setup section)
# 6. Start frontend (not in docker-compose)
cd frontend && npm install && npm run dev

# 7. Check API is running
curl http://localhost:8000/health

# 8. Open frontend
# Visit http://localhost:3000 in your browser
```

**Backend API**: http://localhost:8000  
**Frontend**: http://localhost:3000  
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

# Create .env file
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

### Celery Worker

```bash
cd backend
source venv/bin/activate
celery -A app.core.celery_app worker --loglevel=info
```

**Backend**: http://localhost:8000  
**Frontend**: http://localhost:3000

## Initial Setup (First Time Only)

After starting the backend, you need to create the first client and admin user.

### Using Python Script

Create `backend/create_admin.py`:
```python
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

print(f"Created client: {client.name}")
print(f"Created admin user: {admin.email}")
print("Password: changeme")
```

Run it:
```bash
cd backend
source venv/bin/activate
python create_admin.py
```

### Using API (Alternative)

1. Start backend
2. Visit http://localhost:8000/docs
3. Use `/api/v1/auth/register` endpoint (requires existing admin, or modify to allow first registration)

## First Steps After Setup

### 1. Login to Frontend

1. Visit http://localhost:3000
2. Login with admin credentials
3. You'll be redirected to the dashboard

### 2. Create a Geography

1. Navigate to "Geographies" in the menu
2. Click "Add Geography"
3. Fill in the form:
   - Name: e.g., "New York"
   - Type: City
   - State Code: NY
   - (Optional) County, latitude, longitude
4. Click "Create"

### 3. Add ZIP Codes

You can add ZIP codes via the API or create them when importing data. For now, let's refresh census data which will create ZIP codes automatically.

### 4. Refresh Census Data

1. On the Geographies page, click "Refresh Census" for your geography
2. Wait a few moments for the background job to complete
3. Check the status - data should populate

### 5. Generate a Report

1. Navigate to "Reports" in the menu
2. Fill in the form:
   - Select your geography
   - Enter ZIP codes (comma-separated, e.g., "10001, 10002")
   - Select service category
   - (Optional) Report name
3. Click "Generate Report"
4. View the report and export as JSON or CSV

## Example Workflow

1. **Create Geography**: "San Francisco, CA"
2. **Refresh Census**: Gets demographic data for ZIP codes in SF
3. **Import Property CSV**: Upload property characteristics (see `examples/property_template.csv`)
4. **Import Channels CSV**: Upload channels data (see `examples/channels_template.csv`)
5. **Generate Report**: Create lawn care report for specific ZIP codes
6. **Export Report**: Download as JSON or CSV

## CSV Import Templates

Example CSV files are in the `examples/` folder:
- `property_template.csv` - Property data format
- `events_template.csv` - Events data format
- `channels_template.csv` - Channels data format

**Important**: CSV files must NOT contain PII columns (email, phone, name, address, etc.). See the templates for allowed columns.

## Troubleshooting

### Database Connection Error

- Check PostgreSQL is running
- Verify DATABASE_URL in `.env` file
- Check database exists: `psql -l | grep local_buyer_intelligence`

### Redis Connection Error

- Check Redis is running: `redis-cli ping` should return `PONG`
- Check REDIS_URL in `.env` file

### Migration Errors

- Reset database: `dropdb local_buyer_intelligence && createdb local_buyer_intelligence`
- Re-run migrations: `alembic upgrade head`

### Authentication Errors

- Ensure you've created an admin user (see Initial Setup)
- Check that SECRET_KEY is set in `.env`
- Try logging in again or clearing browser storage

### Frontend Not Connecting to Backend

- Check NEXT_PUBLIC_API_URL in frontend environment
- Ensure backend is running on the correct port
- Check CORS settings in backend (should allow localhost:3000)

## Next Steps

- See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed setup instructions
- See [README.md](README.md) for full documentation
- Check API docs at http://localhost:8000/docs for all available endpoints
