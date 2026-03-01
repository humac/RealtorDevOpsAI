# CLAUDE.md

Project context for AI assistants working on this codebase.

## What This Project Does

RealtorDevOpsAI is an AI-powered real estate development analysis platform for Ottawa, Ontario. It parses Ottawa zoning bylaws, estimates development costs with 2024 local pricing, and uses GPT-4 to generate feasibility scenarios for property investors.

## Build & Run

```bash
# Start all services (PostgreSQL+PostGIS, Redis, backend, frontend)
docker-compose up

# Backend only (requires Postgres + Redis running)
cd backend && pip install -e ".[dev]" && uvicorn app.main:app --reload --port 8000

# Frontend only
cd frontend && npm install && npm run dev
```

## Tests

```bash
cd backend
pytest                    # Run all tests (20 total: 8 zoning + 12 cost engine)
pytest tests/test_zoning_parser.py    # Zoning parser tests only
pytest tests/test_cost_engine.py      # Cost engine tests only
pytest -v                 # Verbose output
```

Tests are pure unit tests — no database, Redis, or external API calls needed.

## Lint

```bash
# Backend
cd backend
ruff check .              # Linting
ruff format --check .     # Format check
mypy .                    # Type checking

# Frontend
cd frontend
npm run lint              # ESLint
npx tsc --noEmit          # TypeScript type check
```

## Architecture

- **Backend**: FastAPI app at `backend/app/main.py`, routes under `backend/app/api/v1/`
- **Frontend**: React 18 + TypeScript + Vite, entry at `frontend/src/main.tsx`
- **Config**: Pydantic settings in `backend/app/core/config.py`, reads from `backend/.env`
- **Database**: SQLAlchemy 2 async models in `backend/app/models/`, migrations via Alembic

### Key Services (backend/app/services/)

| File | Purpose |
|---|---|
| `zoning_parser.py` | Parses Ottawa By-law 2008-250 zone codes (R1–R5, GM, TM, MC, LC, AM), computes building envelopes and development potential |
| `ottawa_cost_engine.py` | Ottawa 2024 cost estimation: construction ($175–$425/sqft by type), teardown, development charges, soft costs (15%), financing, HST |
| `ai_analysis.py` | GPT-4 integration with function calling for structured scenario generation |
| `data_aggregator.py` | Fetches from Ottawa Open Data API and GeoOttawa WFS/WMS services |

### API Routes (backend/app/api/v1/)

| File | Prefix | Purpose |
|---|---|---|
| `analysis.py` | `/api/v1/analyze-property` | Main analysis orchestration endpoint |
| `properties.py` | `/api/v1/properties` | Property CRUD, search, spatial queries |
| `scenarios.py` | `/api/v1/scenarios` | Scenario retrieval and comparison |
| `reports.py` | `/api/v1/reports` | PDF report generation |

### Frontend Components (frontend/src/components/)

| Directory | Key Components |
|---|---|
| `map/` | `PropertyMap.tsx` — Mapbox GL map with zoning overlays |
| `dashboard/` | `AnalysisForm.tsx` — Property search and analysis trigger |
| `analysis/` | `AnalysisPanel.tsx` — Tabbed panel (Overview, Zoning, Costs, Scenarios) |

## Code Conventions

- **Python**: 3.11+, async/await throughout, ruff for linting (line length 100)
- **TypeScript**: Strict mode, functional React components with hooks
- **Testing**: pytest with `asyncio_mode = "auto"`, test files prefixed `test_`
- **Config**: All secrets via environment variables, never hardcoded
- **API versioning**: All routes under `/api/v1/` prefix

## Common Patterns

- Pydantic v2 schemas for request/response validation (`backend/app/schemas/`)
- SQLAlchemy 2.0-style async sessions (`backend/app/core/database.py`)
- Redis caching with configurable TTL (`backend/app/core/cache.py`)
- Ottawa-specific domain constants live in the service files (zone tables, cost rates)
