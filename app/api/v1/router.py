from fastapi import APIRouter
from app.api.v1.endpoints import (
    reports, 
    users, 
    locations,
    verifications,
    auth,
    media)

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=['Users'])
api_router.include_router(reports.router, prefix="/reports", tags=['Reports'])
api_router.include_router(locations.router, prefix="/locations", tags=['Locations'])
api_router.include_router(auth.router, prefix="/auth", tags=['Authentication'])
api_router.include_router(media.router, prefix="/media", tags=['Media'])
api_router.include_router(verifications.router, prefix="/verifications", tags=['Verification'])