"""Deterministic, server-authoritative movement calculation."""

import math

from shooting_fighter_shared.constants import MOVEMENT_SPEED, TICK_INTERVAL, WORLD_MAX, WORLD_MIN
from shooting_fighter_server.entities.player import Player


def update_player_movement(player: Player, dt: float = TICK_INTERVAL) -> None:
    """Apply the player's current input for one simulation step."""
    controls = player.input_state
    forward_axis = float(controls.forward) - float(controls.backward)
    strafe_axis = float(controls.right) - float(controls.left)
    magnitude = math.hypot(forward_axis, strafe_axis)
    if magnitude:
        forward_axis /= magnitude
        strafe_axis /= magnitude

    yaw = math.radians(controls.yaw)
    player.x += (math.sin(yaw) * forward_axis + math.cos(yaw) * strafe_axis) * MOVEMENT_SPEED * dt
    player.z += (math.cos(yaw) * forward_axis - math.sin(yaw) * strafe_axis) * MOVEMENT_SPEED * dt
    player.x = min(WORLD_MAX, max(WORLD_MIN, player.x))
    player.z = min(WORLD_MAX, max(WORLD_MIN, player.z))
    player.yaw = controls.yaw
