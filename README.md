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
# Copy example env files and configure
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### Running the Application

**Backend** (FastAPI):
```bash
cd backend
uvicorn app.main:app --reload
```

**Frontend** (Next.js):
```bash
cd frontend
npm run dev
```

**Celery Worker** (Background Jobs):
```bash
cd backend
celery -A app.core.celery_app worker --loglevel=info
```

## API Documentation

Once running, visit:
- **API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## License

Proprietary - All rights reserved

