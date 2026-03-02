# RealtorDevOpsAI

AI-powered real estate development analysis platform for Ottawa, Ontario. Aggregates municipal zoning data, survey information, and market signals, then uses configurable LLM providers to generate development feasibility studies with cost estimates and profit projections.

## Features

- **Zoning Analysis** — Parses Ottawa By-law 2008-250 for 10+ zone codes (R1–R5, GM, TM, MC, LC, AM) with height/FSI override support
- **Cost Estimation** — Ottawa-specific 2024 pricing: construction, teardown, development charges, soft costs, financing, HST
- **AI Scenarios** — Multi-provider LLM support (OpenAI, Anthropic, Google, Ollama Cloud) with structured output
- **LLM Settings** — In-app settings page to switch providers and models at runtime
- **Sensitivity Analysis** — Monte Carlo simulation across key variables (construction cost, revenue, interest rates)
- **Interactive Map** — Mapbox GL with zoning overlays, parcel boundaries, floodplain, and heritage layers
- **PDF Reports** — Exportable feasibility reports via WeasyPrint

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, Mapbox GL JS |
| Backend | Python 3.11+, FastAPI, SQLAlchemy 2 (async), Pydantic v2 |
| Database | PostgreSQL 15 + PostGIS |
| Cache | Redis 7 |
| AI | OpenAI GPT-4, Anthropic Claude, Google Gemini, Ollama Cloud |
| PDF | WeasyPrint + Jinja2 |

## Prerequisites

- Docker & Docker Compose
- At least one LLM provider API key (OpenAI, Anthropic, Google, or Ollama Cloud)
- Mapbox access token

## Quick Start

1. **Clone and configure environment:**

   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```

   Edit both `.env` files with your API keys.

2. **Start all services:**

   ```bash
   docker-compose up
   ```

   This starts PostgreSQL+PostGIS (port 5432), Redis (port 6379), the backend API (port 8000), and the frontend dev server (port 3000).

3. **Open the app:** http://localhost:3000

4. **API docs:** http://localhost:8000/docs

## Local Development (without Docker)

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

Requires a running PostgreSQL+PostGIS instance and Redis. Configure `DATABASE_URL` and `REDIS_URL` in `backend/.env`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Dev server runs at http://localhost:5173.

### Running Tests

```bash
cd backend
pytest
```

Tests cover the zoning parser (8 tests) and cost engine (12 tests). No external services required.

### Linting

```bash
# Backend
cd backend
ruff check .
mypy .

# Frontend
cd frontend
npm run lint
```

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/analyze-property` | Full development analysis with AI scenarios |
| `GET` | `/api/v1/properties/search?q=` | Search by address, MLS, or parcel ID |
| `GET` | `/api/v1/properties/filter` | Filter by ward, zoning, lot size, value |
| `GET` | `/api/v1/properties/nearby?lat=&lng=` | Spatial search (PostGIS) |
| `GET` | `/api/v1/properties/{id}` | Property details |
| `GET` | `/api/v1/scenarios/property/{id}` | Scenarios for a property |
| `POST` | `/api/v1/scenarios/compare` | Side-by-side scenario comparison |
| `GET` | `/api/v1/reports/property/{id}/pdf` | Generate PDF report |
| `GET` | `/api/v1/llm-settings` | Get current LLM provider settings |
| `PUT` | `/api/v1/llm-settings` | Update active LLM provider and model |
| `GET` | `/health` | Health check |

See full OpenAPI spec at [`openapi.yaml`](openapi.yaml) or at `/docs` when running.

## Project Structure

```
backend/
├── app/
│   ├── api/v1/          # Route handlers (analysis, properties, scenarios, reports, llm-settings)
│   ├── core/            # Config, database, cache
│   ├── models/          # SQLAlchemy models (property, scenario, zoning)
│   ├── schemas/         # Pydantic request/response schemas
│   └── services/        # Business logic
│       ├── zoning_parser.py        # Ottawa By-law 2008-250 parser
│       ├── ottawa_cost_engine.py   # Cost estimation with 2024 pricing
│       ├── ai_analysis.py          # Multi-provider LLM scenario generation
│       └── data_aggregator.py      # Ottawa Open Data & GeoOttawa client
├── tests/               # pytest test suite
├── alembic/             # Database migrations
├── Dockerfile
└── pyproject.toml

frontend/
├── src/
│   ├── components/
│   │   ├── analysis/    # AnalysisPanel, OverviewTab, ZoningTab, CostsTab, ScenariosTab
│   │   ├── common/      # Header
│   │   ├── dashboard/   # AnalysisForm
│   │   ├── map/         # PropertyMap (Mapbox GL)
│   │   └── settings/    # SettingsPage (LLM provider config)
│   ├── hooks/           # useAnalysis
│   ├── services/        # API client (axios)
│   ├── types/           # TypeScript interfaces
│   └── utils/           # Formatting helpers
├── Dockerfile
└── package.json
```

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL+PostGIS connection string |
| `REDIS_URL` | Redis connection string |
| `LLM_PROVIDER` | Active LLM provider: `openai`, `anthropic`, `google`, or `ollama` (default: `openai`) |
| `OPENAI_API_KEY` | OpenAI API key |
| `OPENAI_MODEL` | OpenAI model (default: `gpt-4`) |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `ANTHROPIC_MODEL` | Anthropic model (default: `claude-sonnet-4-20250514`) |
| `GOOGLE_API_KEY` | Google AI API key |
| `GOOGLE_MODEL` | Google model (default: `gemini-2.0-flash`) |
| `OLLAMA_BASE_URL` | Ollama Cloud URL (default: `https://cloud.ollama.com`) |
| `OLLAMA_API_KEY` | Ollama Cloud API key |
| `OLLAMA_MODEL` | Ollama model (default: `llama3`) |
| `OTTAWA_OPEN_DATA_URL` | Ottawa Open Data API base URL |
| `GEO_OTTAWA_WFS_URL` | GeoOttawa WFS endpoint |
| `GEO_OTTAWA_WMS_URL` | GeoOttawa WMS endpoint |
| `MAPBOX_ACCESS_TOKEN` | Mapbox token for geocoding |
| `AUTH0_DOMAIN` | Auth0 tenant domain |
| `AUTH0_API_AUDIENCE` | Auth0 API audience |

### Frontend (`frontend/.env`)

| Variable | Description |
|---|---|
| `VITE_API_URL` | Backend API URL (default: `http://localhost:8000`) |
| `VITE_MAPBOX_TOKEN` | Mapbox access token |

## License

Proprietary. All rights reserved.
