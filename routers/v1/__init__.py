from fastapi import APIRouter
from .jobs import router as jobs_router
from .admin import router as admin_router

router = APIRouter(prefix="/v1")
router.include_router(jobs_router)
router.include_router(admin_router)