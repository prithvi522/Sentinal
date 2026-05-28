from fastapi import APIRouter

from app.api.v1.endpoints import auth, copilot, dashboard, demo, incidents, intelligence, prompts, reports, security, threats, websocket


api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(security.router, prefix="/security", tags=["security"])
api_router.include_router(intelligence.router, prefix="/intelligence", tags=["intelligence"])
api_router.include_router(prompts.router, prefix="/prompt-firewall", tags=["prompt-firewall"])
api_router.include_router(threats.router, prefix="/threats", tags=["threats"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
api_router.include_router(copilot.router, prefix="/copilot", tags=["copilot"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(demo.router, prefix="/demo", tags=["demo"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(websocket.router, prefix="/ws", tags=["websocket"])
