# Architecture Overview

## System Architecture

The Local Buyer Intelligence Platform is built with a modular, service-oriented architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js)                      │
│  - React components                                          │
│  - Mapbox visualizations                                     │
│  - Report generation UI                                      │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP/REST API
┌───────────────────────▼─────────────────────────────────────┐
│                   Backend (FastAPI)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   API Layer  │  │  Services    │  │  Collectors  │      │
│  │  (Endpoints) │  │  (Business   │  │  (Data       │      │
│  │              │  │   Logic)     │  │   Sources)   │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
│         └──────────────────┼──────────────────┘              │
│                            │                                 │
│                   ┌────────▼────────┐                        │
│                   │   Database      │                        │
│                   │  (PostgreSQL)   │                        │
│                   └─────────────────┘                        │
└─────────────────────────────────────────────────────────────┘
                        │
         ┌──────────────┼──────────────┐
         │              │              │
    ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
    │  Redis  │   │  Celery │   │ External│
    │ (Cache) │   │ (Tasks) │   │   APIs  │
    └─────────┘   └─────────┘   └─────────┘
```

## Core Components

### 1. Backend API Layer

**Location**: `backend/app/api/v1/endpoints/`

- `geography.py`: Geographic data management (cities, ZIP codes, neighborhoods)
- `households.py`: Household data endpoints (non-PII)
- `intelligence.py`: Intelligence report generation and retrieval
- `demand_signals.py`: Demand signal management (events, permits, etc.)

### 2. Services Layer

**Location**: `backend/app/services/`

- `intelligence_engine.py`: Core intelligence engine
  - Demand score calculation
  - Buyer profile generation
  - ZIP code demand scoring
  - Channel and timing recommendations

### 3. Data Models

**Location**: `backend/app/models/`

- `geography.py`: Geographic entities (Geography, ZIPCode, Neighborhood)
- `household.py`: Household records (non-PII property characteristics)
- `demand_signal.py`: Demand signals (events, permits, seasonal indicators)
- `intelligence_report.py`: Generated intelligence reports

### 4. Data Collectors

**Location**: `backend/app/collectors/`

- `base_collector.py`: Base class for all collectors
- `census_collector.py`: Census data collection (aggregate statistics)
- `property_collector.py`: Property assessor data (property characteristics only)
- `event_collector.py`: Public event calendars

**Principles**:
- No PII collection (names, emails, phone numbers)
- Only public data sources
- Respect robots.txt and rate limits
- Aggregate data where possible

### 5. Frontend

**Location**: `frontend/src/`

- `pages/index.tsx`: Main dashboard
- `components/IntelligenceReportGenerator.tsx`: Report generation form
- `components/MapVisualization.tsx`: Mapbox integration for visualizations
- `components/DemandHeatmap.tsx`: Demand score visualizations

## Data Flow

### Intelligence Report Generation

```
1. User Request (Frontend/API)
   ↓
2. Intelligence Engine Service
   ├─ Fetch households by geography
   ├─ Calculate demand scores
   ├─ Generate buyer profile
   ├─ Calculate ZIP demand scores
   └─ Generate recommendations
   ↓
3. Store Report (Database)
   ↓
4. Return Response (JSON)
```

### Data Collection Flow

```
1. Scheduled Task (Celery) or Manual Trigger
   ↓
2. Collector Instance
   ├─ Collect data from source
   ├─ Validate data
   └─ Store in database
   ↓
3. Database (Households, DemandSignals, etc.)
```

## Database Schema

### Core Tables

- **geographies**: Cities, states, counties
- **zip_codes**: ZIP code data with aggregate statistics
- **neighborhoods**: Neighborhood-level geographic entities
- **households**: Property/household characteristics (non-PII)
- **demand_signals**: Events, permits, seasonal indicators
- **intelligence_reports**: Generated reports with buyer profiles and recommendations

### Key Relationships

```
Geography (1) ──< (M) ZIPCode
Geography (1) ──< (M) Neighborhood
ZIPCode (1) ──< (M) Household
ZIPCode (1) ──< (M) DemandSignal
Geography (1) ──< (M) IntelligenceReport
```

## Security & Privacy

### Data Privacy Principles

1. **No PII Storage**: Never store names, emails, phone numbers of individuals
2. **Aggregate Data**: Use census blocks, ZIP codes, and aggregated statistics
3. **Public Data Only**: Only collect from public, open data sources
4. **Respect robots.txt**: Always check and respect robots.txt files
5. **Rate Limiting**: Implement rate limits for external API calls

### Authentication (Future)

- Simple role-based authentication (admin/client)
- JWT tokens for API access
- API key authentication for collectors

## Scalability Considerations

### Current Architecture

- Single database instance (PostgreSQL)
- In-memory processing for intelligence calculations
- Synchronous API endpoints

### Future Enhancements

- **Caching**: Redis caching for frequently accessed data
- **Background Processing**: Celery tasks for large report generation
- **Database Sharding**: Shard by geography for very large datasets
- **CDN**: Serve static frontend assets via CDN
- **Load Balancing**: Multiple backend instances behind load balancer

## Technology Choices

### Backend

- **FastAPI**: Modern, fast Python web framework with automatic API docs
- **SQLAlchemy**: ORM for database interactions
- **Alembic**: Database migration management
- **Celery**: Distributed task queue for background jobs
- **Pydantic**: Data validation and settings management

### Frontend

- **Next.js**: React framework with SSR and routing
- **TypeScript**: Type safety
- **Tailwind CSS**: Utility-first CSS framework
- **Mapbox GL**: Interactive maps and visualizations
- **Recharts**: Chart library for data visualization

### Database

- **PostgreSQL**: Relational database with geographic extensions support

### Infrastructure

- **Docker**: Containerization for easy deployment
- **Redis**: Caching and Celery broker
- **Docker Compose**: Local development orchestration

## API Design

### RESTful Principles

- Resource-based URLs (`/api/v1/households/`, `/api/v1/intelligence/reports/`)
- HTTP methods (GET, POST, PUT, DELETE)
- JSON request/response format
- Proper HTTP status codes

### API Versioning

- Current version: `v1`
- Versioned via URL path: `/api/v1/`
- Future versions: `/api/v2/`, etc.

## Extension Points

### Adding New Service Categories

1. Add enum value to `ServiceCategory` in `demand_signal.py`
2. Add scoring logic in `intelligence_engine.py`
3. Update frontend dropdowns/components

### Adding New Data Sources

1. Create new collector class extending `BaseCollector`
2. Implement `collect()`, `validate_data()`, and `store()` methods
3. Register collector in Celery tasks (if automated)
4. Add API endpoint if manual collection is needed

### Customizing Demand Scoring

Modify methods in `IntelligenceEngine` class:
- `calculate_household_demand_score()`: Main scoring logic
- Category-specific methods: `_calculate_lawn_care_score()`, etc.

## Monitoring & Logging

### Current State

- Basic logging via Python's logging module
- Console output for development

### Future Enhancements

- Structured logging (JSON format)
- Log aggregation (ELK stack, CloudWatch, etc.)
- Application performance monitoring (APM)
- Error tracking (Sentry, Rollbar, etc.)






