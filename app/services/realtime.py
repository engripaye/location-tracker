from collections import defaultdict
from uuid import UUID

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.connections: dict[UUID, set[WebSocket]] = defaultdict(set)

    async def connect(self, session_id: UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections[session_id].add(websocket)

    def disconnect(self, session_id: UUID, websocket: WebSocket) -> None:
        self.connections[session_id].discard(websocket)
        if not self.connections[session_id]:
            self.connections.pop(session_id, None)

    async def broadcast(self, session_id: UUID, payload: dict) -> None:
        stale: list[WebSocket] = []
        for websocket in self.connections.get(session_id, set()):
            try:
                await websocket.send_json(payload)
            except RuntimeError:
                stale.append(websocket)
        for websocket in stale:
            self.disconnect(session_id, websocket)


manager = ConnectionManager()
