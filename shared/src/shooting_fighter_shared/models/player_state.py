"""Authoritative player position included in snapshots."""

from pydantic import BaseModel, ConfigDict, Field


class PlayerState(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str = Field(min_length=1, max_length=64)
    x: float = Field(ge=-20.0, le=20.0)
    y: float = Field(ge=0.0, le=10.0)
    z: float = Field(ge=-20.0, le=20.0)
    yaw: float = Field(ge=0.0, lt=360.0)
