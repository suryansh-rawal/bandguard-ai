from fastapi import APIRouter
from app.api.v1.endpoints import auth, analyze, documents, reviews, health

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(analyze.router)
api_router.include_router(documents.router)
api_router.include_router(reviews.router)
