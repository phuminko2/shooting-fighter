"""Ursina entry point; networking runs outside the render thread."""

from typing import Any

from shooting_fighter_shared.messages import PlayerInputPayload, SnapshotMessage, WelcomeMessage
from shooting_fighter_client.config.settings import SERVER_URL
from shooting_fighter_client.networking.network_client import NetworkClient
from shooting_fighter_client.scenes.arena import build_arena


def run() -> None:
    from ursina import Ursina, Entity, Text, camera, color, held_keys, mouse, window

    app = Ursina()
    window.title = "Shooting Fighter"
    build_arena()
    camera.position = (0, 1.6, -3)
    camera.rotation = (0, 0, 0)
    mouse.locked = True
    status = Text(text="Connecting...", position=(-0.85, 0.46), scale=0.8)
    network = NetworkClient(SERVER_URL)
    network.start()
    player_id: str | None = None
    remote_entities: dict[str, Any] = {}
    yaw = 0.0

    def update() -> None:
        nonlocal player_id, yaw
        while not network.events.empty():
            event = network.events.get()
            if isinstance(event, WelcomeMessage):
                player_id = event.player_id
                status.text = f"Connected as {player_id} in {event.room}"
            elif isinstance(event, SnapshotMessage):
                present: set[str] = set()
                for player in event.players:
                    if player.id == player_id:
                        camera.position = (player.x, player.y + 0.6, player.z)
                        continue
                    present.add(player.id)
                    entity = remote_entities.get(player.id)
                    if entity is None:
                        entity = Entity(
                            model="cube",
                            scale=(0.7, 2.0, 0.7),
                            color=color.azure,
                        )
                        remote_entities[player.id] = entity
                    entity.position = (player.x, player.y, player.z)
                    entity.rotation_y = player.yaw
                for removed_id in set(remote_entities) - present:
                    remote_entities.pop(removed_id).disable()
            elif isinstance(event, tuple):
                status.text = str(event[1])

        if not player_id:
            return
        yaw = (yaw + mouse.velocity.x * 100) % 360
        camera.rotation_y = yaw
        network.submit_input(
            PlayerInputPayload(
                forward=bool(held_keys["w"]),
                backward=bool(held_keys["s"]),
                left=bool(held_keys["a"]),
                right=bool(held_keys["d"]),
                yaw=yaw,
            )
        )

    updater = Entity()
    updater.update = update
    app.run()


if __name__ == "__main__":
    run()
