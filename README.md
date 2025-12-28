# Local Buyer Intelligence & Lead Generation Platform

A suite of apps that help **local businesses** identify, reach, and convert **potential customers in specific geographic areas** across many service verticals, **without scraping or storing private personal PII**.

## System Overview

The platform consists of **5 coordinated apps/modules**:

1. **Local Buyer Intelligence Platform** (This Module) ⭐
2. **Lead Funnel & Opt-In Capture Builder**
3. **Public Data & Signal Scraper**
4. **Institutional Channel Mapper (Gatekeeper Access)**
5. **Campaign Orchestration & Monetization Engine**

## Shared Principles (Non-Negotiable)

- ✅ Do NOT scrape or store personal phone numbers/emails of private individuals
- ✅ Do NOT bypass logins, CAPTCHAs, or robots.txt
- ✅ Data focus = **households, signals, institutions, timing, channels**
- ✅ Output = **actionable marketing access**, not raw PII
- ✅ Everything must be **geo-scoped** (city, ZIP, neighborhood)

## Tech Stack

- **Backend**: Python (FastAPI)
- **Frontend**: React/Next.js
- **Database**: PostgreSQL
- **Background Jobs**: Celery + Redis
- **Maps**: Mapbox
- **Messaging** (opt-in only): Twilio / email provider
- **Auth**: Simple role-based (admin / client)

## Module 1: Local Buyer Intelligence Platform

### Purpose
Answer: *"Where are potential buyers in this city, and how do we reach them?"*

### Inputs
- City / State / ZIP(s)
- Service category (fireworks, lawn care, security, IT, etc.)
- Time window (seasonal)

### Data Sources (Allowed)
- Property tax / assessor records (public)
- Census-derived aggregates
- Event calendars (city, schools, parks)
- Permit filings (where applicable)
- Housing turnover indicators
- Weather + seasonality

### Core Features
- Household segmentation (non-PII):
  - Homeowner vs renter
  - Property type
  - Yard size proxy
  - Income band proxy
- Demand indicators by service
- Neighborhood heatmaps
- Seasonal demand scoring

### Output (Sellable)
- "Buyer profile" by neighborhood
- ZIP-level demand score
- Channel recommendations
- Timing recommendations

## Project Structure

```
local-buyer-intelligence/
├── backend/               # FastAPI application
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic
│   │   ├── collectors/   # Data collection modules
│   │   └── core/         # Config, security, etc.
│   ├── alembic/          # Database migrations
│   └── requirements.txt
├── frontend/              # React/Next.js application
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── utils/
│   └── package.json
├── shared/                # Shared data models/types
├── scripts/               # Utility scripts
├── docker-compose.yml     # Local development setup
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- Redis (for Celery)

### Installation

1. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Database Setup**
```bash
# Create database
createdb local_buyer_intelligence

# Run migrations
cd backend
alembic upgrade head
```

3. **Frontend Setup**
```bash
cd frontend
npm install
```

4. **Environment Variables**
```bash
# Backend - Create backend/.env file:
DATABASE_URL=postgresql://user:password@localhost:5432/local_buyer_intelligence
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here-change-in-production
MAPBOX_ACCESS_TOKEN=your_mapbox_token_here
ENVIRONMENT=development

# Frontend - Create frontend/.env.local (optional):
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_MAPBOX_TOKEN=your_mapbox_token_here
```

### Initial Setup (First Time)

1. **Create First Client and Admin User**

You'll need to create the first client and admin user. You can do this via the API:

```bash
# Start the backend first
cd backend
uvicorn app.main:app --reload

# In another terminal, create client and user (Python script or API call)
# Or use the interactive API docs at http://localhost:8000/docs
```

Or use Python:
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
```

### Running the Application

**Start PostgreSQL and Redis** (if not using Docker):
```bash
# PostgreSQL
# Ensure PostgreSQL is running on port 5432

# Redis
redis-server
```

**Backend** (FastAPI):
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload
```

**Celery Worker** (Background Jobs - in separate terminal):
```bash
cd backend
source venv/bin/activate
celery -A app.core.celery_app worker --loglevel=info
```

**Frontend** (Next.js - in separate terminal):
```bash
cd frontend
npm run dev
```

### Accessing the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

**Login**: Use the admin credentials you created during initial setup.

## Key Features

### Multi-Tenancy
- All data is scoped by `client_id`
- Users belong to clients (or are global admins)
- Complete data isolation between clients

### PII Compliance
- **No personal identifiers stored** (email, phone, name, address, etc.)
- PII Guard validates all imports
- CSV headers checked for disallowed fields
- Only aggregated/geographic data

### Data Ingestion

1. **Census Data**: Automated refresh via Census API (ACS 5-year estimates)
2. **CSV Imports**: Upload CSV files for:
   - Property data (non-PII characteristics)
   - Events (public event calendars)
   - Channels (institutional/gatekeeper data)

3. **Background Processing**: All imports processed asynchronously via Celery

### Intelligence Reports

Generate reports that include:
- Buyer profiles (aggregated, non-PII)
- ZIP code demand scores
- Channel recommendations
- Timing recommendations
- Export as JSON or CSV

## Workflow

1. **Create Geography**: Add a city/county/state
2. **Refresh Census Data**: Pull demographic data for ZIP codes
3. **Import Property Data**: Upload CSV with property characteristics
4. **Import Channels**: Upload CSV with institutional channels (HOAs, schools, etc.)
5. **Generate Report**: Create intelligence report for a service category
6. **Export**: Download report as JSON or CSV

## License

Proprietary - All rights reserved

