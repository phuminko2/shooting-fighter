# Shooting Fighter

Milestone 1 multiplayer prototype: an authoritative FastAPI server and an Ursina client share a versioned JSON WebSocket protocol.

## Workspace

The root uv workspace contains three independently packaged projects:

- `game-server`: FastAPI transport, room lifecycle, and fixed-step authoritative simulation.
- `game-client`: Ursina arena and background-thread WebSocket client.
- `shared`: Protocol v1 models and simulation/world constants; no rendering or transport dependencies.

All packages use `src/` layouts. The client and server consume `shooting-fighter-shared` through uv workspace dependencies and the root `uv.lock`.

## Run

Install/sync the workspace from the repository root:

```sh
uv sync --all-packages
```

In one terminal, start the server:

```sh
uv run --package shooting-fighter-server shooting-fighter-server
```

In two other terminals, start independent clients:

```sh
uv run --package shooting-fighter-client shooting-fighter-client
```

The default server address is `ws://127.0.0.1:8000/ws`. Configure the server bind address with `SHOOTING_FIGHTER_HOST` and `SHOOTING_FIGHTER_PORT`, and the client URL with `SHOOTING_FIGHTER_SERVER`.

## Controls and protocol conventions

- WASD moves relative to camera yaw; the mouse turns the camera.
- Coordinates are Y-up. Player origin is at the center of the 2-unit-tall body, with spawn `y=1`.
- X/Z boundaries are `[-20, 20]`; movement speed is 5 world units/second.
- Yaw is degrees in `[0, 360)`: 0 faces +Z and increasing yaw turns toward +X.
- The server simulates at 20 Hz and broadcasts snapshots at 10 Hz. Rooms hold up to four players.

## Verify and test

```sh
uv run --all-packages pytest
```

Manual multiplayer check: start the server, then two graphical client processes. Both clients should see the other player's blue cube. Move with WASD and turn with the mouse; disconnect one client and its cube should disappear from the next snapshot.

The client requires a graphical display. Headless tests cover shared messages and simulation/room logic without opening Ursina.

## Current milestone

Milestone 1 — Multiplayer Foundation. Combat, persistence, authentication, and later controller/network optimizations are out of scope.
