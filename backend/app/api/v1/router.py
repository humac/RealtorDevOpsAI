from fastapi import APIRouter

from app.api.v1 import properties, analysis, scenarios, reports

api_router = APIRouter()
api_router.include_router(properties.router, prefix="/properties", tags=["properties"])
api_router.include_router(analysis.router, prefix="/analyze-property", tags=["analysis"])
api_router.include_router(scenarios.router, prefix="/scenarios", tags=["scenarios"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
