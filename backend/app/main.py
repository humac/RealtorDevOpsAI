"""RealtorDevOpsAI - Real Estate Development Analysis Platform."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    description=(
        "AI-powered real estate development analysis platform for Ottawa, Ontario. "
        "Identifies properties with development potential by aggregating municipal data, "
        "zoning bylaws, and survey information, then uses AI to generate feasibility studies, "
        "cost estimates, and profit projections."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.app_name}
