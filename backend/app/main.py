import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import Base, SessionLocal, engine
from app.middleware.security import SecurityMiddleware
from app.models.threat_event import ThreatEvent
from app.services.simulation import simulated_attack_event
from app.services.websocket_manager import ws_manager


app = FastAPI(title=settings.app_name)

# Allow the frontend during development. Be restrictive in production.
if settings.environment == "development":
    allow_origins = [
        settings.frontend_origin,
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:5174",
        "http://localhost:5174",
        # Added your Network IPs from Vite's server outputs:
        "http://192.168.31.40:5173", 
        "http://192.168.31.40:5174",
    ]
else:
    allow_origins = [settings.frontend_origin]

# CORSMiddleware must be evaluated cleanly by the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# During development, Vite may pick random localhost ports (5173, 5174, 5175, 5176, etc.).
# Allow any localhost origin on any port using a regex so preflight checks succeed.
if settings.environment == "development":
    # note: allow_origin_regex is evaluated when allow_origins is empty or used alongside it.
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"^http://localhost(:[0-9]+)?$|^http://127.0.0.1(:[0-9]+)?$",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_middleware(SecurityMiddleware)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok", "service": settings.app_name}


async def simulation_loop():
    while True:
        event = simulated_attack_event()
        db = SessionLocal()
        try:
            db_event = ThreatEvent(
                event_type=event["event_type"],
                source_ip=event["source_ip"],
                severity=event["severity"],
                confidence=event["confidence"],
                description=event["description"],
                event_metadata=event["metadata"],
            )
            db.add(db_event)
            db.commit()
        finally:
            db.close()

        await ws_manager.broadcast_json({"channel": "simulation_alert", "payload": event})
        await asyncio.sleep(settings.simulation_interval_seconds)


@app.on_event("startup")
async def on_startup():
    Base.metadata.create_all(bind=engine)
    app.state.simulation_task = asyncio.create_task(simulation_loop())


@app.on_event("shutdown")
async def on_shutdown():
    task = getattr(app.state, "simulation_task", None)
    if task:
        task.cancel()