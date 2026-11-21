"""Minimal in-memory room lookup and lifecycle."""

from shooting_fighter_shared.constants import ROOM_NAME
from shooting_fighter_server.rooms.room import Room


class RoomManager:
    def __init__(self) -> None:
        self._rooms = {ROOM_NAME: Room()}

    def get_room(self, name: str = ROOM_NAME) -> Room:
        try:
            return self._rooms[name]
        except KeyError as exc:
            raise ValueError(f"unknown room: {name}") from exc
