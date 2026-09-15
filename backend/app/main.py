from __future__ import annotations

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, ConfigDict


class TacticalAlert(BaseModel):
    type: str
    severity: str
    timestamp: str
    title: str
    description: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "TACTICAL_ALERT",
                "severity": "HIGH",
                "timestamp": "00:34:21",
                "title": "Exploração do corredor esquerdo",
                "description": "A equipe adversária está criando superioridade numérica pelo lado esquerdo.",
            }
        }
    )


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self._connections:
            self._connections.remove(websocket)

    async def broadcast(self, message: dict[str, str]) -> None:
        disconnected: list[WebSocket] = []
        for connection in self._connections:
            try:
                await connection.send_json(message)
            except RuntimeError:
                disconnected.append(connection)

        for connection in disconnected:
            self.disconnect(connection)


app = FastAPI(title="VARZIA Backend")
manager = ConnectionManager()


@app.websocket("/ws/events")
async def events_websocket(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.post("/events", status_code=201)
async def create_event(event: TacticalAlert) -> dict[str, object]:
    payload = event.model_dump()
    await manager.broadcast(payload)
    return {"status": "broadcasted", "event": payload}
