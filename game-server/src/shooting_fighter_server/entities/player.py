"""Server-side player data, including the latest validated input."""

from dataclasses import dataclass, field

from shooting_fighter_shared.messages import PlayerInputPayload


@dataclass
class Player:
    player_id: str
    x: float
    y: float = 1.0
    z: float = 0.0
    yaw: float = 0.0
    last_sequence: int = 0
    input_state: PlayerInputPayload = field(
        default_factory=lambda: PlayerInputPayload(yaw=0.0)
    )
