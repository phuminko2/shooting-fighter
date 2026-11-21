"""FastAPI WebSocket transport for the authoritative game room."""

import json
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from shooting_fighter_shared.constants import MAX_MESSAGE_BYTES, ROOM_NAME
from shooting_fighter_shared.messages import InputMessage
from shooting_fighter_server.core.config import ServerConfig
from shooting_fighter_server.rooms.room_manager import RoomManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
rooms = RoomManager()


@asynccontextmanager
async def lifespan(_: FastAPI):
    room = rooms.get_room()
    room.start()
    yield
    await room.stop()


app = FastAPI(title="Shooting Fighter Server", lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    room = rooms.get_room(ROOM_NAME)
    try:
        player = room.join(websocket)
    except ValueError:
        await websocket.send_json({"type": "error", "code": "room_full", "message": "Room is full"})
        await websocket.close(code=1008)
        return

    logger.info("Player %s joined %s", player.player_id, room.name)
    try:
        await websocket.send_json(
            {
                "type": "welcome",
                "protocol_version": 1,
                "player_id": player.player_id,
                "room": room.name,
            }
        )
        await room.broadcast_event({"type": "player_joined", "player_id": player.player_id})
        while True:
            raw = await websocket.receive_text()
            if len(raw.encode("utf-8")) > MAX_MESSAGE_BYTES:
                await websocket.send_json(
                    {"type": "error", "code": "message_too_large", "message": "Message exceeds limit"}
                )
                continue
            try:
                message = InputMessage.model_validate_json(raw)
            except ValidationError:
                await websocket.send_json(
                    {"type": "error", "code": "invalid_message", "message": "Invalid input message"}
                )
                continue
            if not room.accept_input(player.player_id, message):
                await websocket.send_json(
                    {"type": "error", "code": "invalid_sequence", "message": "Sequence must increase"}
                )
    except WebSocketDisconnect:
        pass
    except (RuntimeError, json.JSONDecodeError):
        logger.info("Connection closed for player %s", player.player_id)
    finally:
        if room.leave(player.player_id):
            logger.info("Player %s left %s", player.player_id, room.name)
            await room.broadcast_event({"type": "player_left", "player_id": player.player_id})


def run() -> None:
    config = ServerConfig.from_environment()
    uvicorn.run("shooting_fighter_server.main:app", host=config.host, port=config.port, reload=False)


if __name__ == "__main__":
    run()
