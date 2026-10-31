from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title="Subscription Intelligence Platform",
    description="Unified Subscription Intelligence & Revenue Management Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "subscription-intelligence-platform"}


@app.get("/")
async def root():
    return {"message": "Subscription Intelligence Platform API"}

from app.modules.auth.router import router as auth_router
app.include_router(auth_router, prefix="/api/v1")
