# Shooting Fighter Server

Run from the repository root with `uv run --package shooting-fighter-server shooting-fighter-server`. The server listens on `127.0.0.1:8000` by default. Set `SHOOTING_FIGHTER_HOST` or `SHOOTING_FIGHTER_PORT` to configure it. WebSocket clients connect at `/ws`; `GET /health` provides a simple health response.
