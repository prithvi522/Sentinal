from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.models.user import User
from app.services.unidirectional.engine import SCENARIOS, traffic_engine


router = APIRouter()


class DemoRequest(BaseModel):
    scenario: str = Field("normal")
    speed: float = Field(1.0, ge=0.5, le=5.0)


@router.get("/overview")
def overview(_: User = Depends(get_current_user)):
    return traffic_engine.overview()


@router.get("/scenarios")
def scenarios(_: User = Depends(get_current_user)):
    return {"scenarios": SCENARIOS, "speeds": [0.5, 1, 2, 5]}


@router.post("/demo/start")
async def start_demo(payload: DemoRequest, _: User = Depends(get_current_user)):
    try:
        return await traffic_engine.start(payload.scenario, payload.speed)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/demo/pause")
async def pause_demo(_: User = Depends(get_current_user)):
    return await traffic_engine.pause()


@router.post("/demo/stop")
async def stop_demo(_: User = Depends(get_current_user)):
    return await traffic_engine.stop()


@router.post("/demo/reset")
def reset_demo(_: User = Depends(get_current_user)):
    return traffic_engine.reset()


@router.websocket("/ws")
async def traffic_socket(websocket: WebSocket):
    await traffic_engine.ws.connect(websocket)
    try:
        await websocket.send_json({"channel": "unidirectional_update", "payload": traffic_engine.overview()})
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        traffic_engine.ws.disconnect(websocket)
