"""Client settings loaded from environment variables."""

import os


SERVER_URL = os.getenv("SHOOTING_FIGHTER_SERVER", "ws://127.0.0.1:8000/ws")
