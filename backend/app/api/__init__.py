"""API routers package."""

from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.commercial import router as commercial_router
from app.api.enquiries import router as enquiries_router
from app.api.masters import router as masters_router
from app.api.quotations import router as quotations_router
from app.api.reports import router as reports_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(masters_router)
api_router.include_router(enquiries_router)
api_router.include_router(quotations_router)
api_router.include_router(commercial_router)
api_router.include_router(reports_router)
