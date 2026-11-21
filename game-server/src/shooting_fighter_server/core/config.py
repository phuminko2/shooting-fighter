"""Server configuration from environment variables."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ServerConfig:
    host: str = "127.0.0.1"
    port: int = 8000

    @classmethod
    def from_environment(cls) -> "ServerConfig":
        return cls(
            host=os.getenv("SHOOTING_FIGHTER_HOST", "127.0.0.1"),
            port=int(os.getenv("SHOOTING_FIGHTER_PORT", "8000")),
        )
