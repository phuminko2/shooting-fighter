"""In-memory battle room and authoritative simulation."""

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from shooting_fighter_shared.constants import (
    MAX_PLAYERS_PER_ROOM,
    ROOM_NAME,
    SNAPSHOT_RATE,
    TICK_INTERVAL,
)
from shooting_fighter_shared.messages import (
    InputMessage,
    PlayerInputPayload,
    SnapshotMessage,
)
from shooting_fighter_shared.models.player_state import PlayerState
from shooting_fighter_server.entities.player import Player
from shooting_fighter_server.systems.movement_system import update_player_movement

logger = logging.getLogger(__name__)


@dataclass
class Room:
    name: str = ROOM_NAME
    max_players: int = MAX_PLAYERS_PER_ROOM
    players: dict[str, Player] = field(default_factory=dict)
    connections: dict[str, Any] = field(default_factory=dict)
    tick: int = 0
    _simulation_task: asyncio.Task[None] | None = field(default=None, init=False, repr=False)

    def join(self, connection: Any) -> Player:
        if len(self.players) >= self.max_players:
            raise ValueError("room is full")
        player_id = uuid.uuid4().hex[:12]
        spawn_x = float((len(self.players) % 2) * 4 - 2)
        player = Player(player_id=player_id, x=spawn_x)
        self.players[player_id] = player
        self.connections[player_id] = connection
        return player

    def leave(self, player_id: str) -> bool:
        self.connections.pop(player_id, None)
        return self.players.pop(player_id, None) is not None

    def accept_input(self, player_id: str, message: InputMessage) -> bool:
        player = self.players.get(player_id)
        if player is None or message.sequence <= player.last_sequence:
            return False
        player.last_sequence = message.sequence
        player.input_state = message.payload
        return True

    def step(self) -> None:
        self.tick += 1
        for player in self.players.values():
            update_player_movement(player)

    def snapshot(self) -> SnapshotMessage:
        return SnapshotMessage(
            tick=self.tick,
            players=[
                PlayerState(id=p.player_id, x=p.x, y=p.y, z=p.z, yaw=p.yaw)
                for p in self.players.values()
            ],
        )

    async def run(self) -> None:
        """Run fixed-step simulation with bounded catch-up on a monotonic clock."""
        next_tick = time.monotonic() + TICK_INTERVAL
        snapshot_ticks = max(1, round((1 / SNAPSHOT_RATE) / TICK_INTERVAL))
        while True:
            delay = next_tick - time.monotonic()
            if delay > 0:
                await asyncio.sleep(delay)
            now = time.monotonic()
            self.step()
            if self.tick % snapshot_ticks == 0:
                snapshot = self.snapshot().model_dump_json()
                await asyncio.gather(
                    *(self._send(connection, snapshot) for connection in tuple(self.connections.values())),
                    return_exceptions=True,
                )
            # Discard excess backlog after one catch-up step to keep ticks bounded.
            next_tick = max(next_tick + TICK_INTERVAL, now + TICK_INTERVAL)

    @staticmethod
    async def _send(connection: Any, message: str) -> None:
        try:
            await connection.send_text(message)
        except Exception:
            logger.debug("Failed to send room message", exc_info=True)

    def start(self) -> None:
        if self._simulation_task is None or self._simulation_task.done():
            self._simulation_task = asyncio.create_task(self.run())

    async def stop(self) -> None:
        if self._simulation_task is not None:
            self._simulation_task.cancel()
            await asyncio.gather(self._simulation_task, return_exceptions=True)
            self._simulation_task = None

    async def broadcast_event(self, event: dict[str, str]) -> None:
        message = json.dumps(event)
        await asyncio.gather(
            *(self._send(connection, message) for connection in tuple(self.connections.values())),
            return_exceptions=True,
        )
