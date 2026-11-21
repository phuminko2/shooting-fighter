"""Protocol v1 message schemas and parsing helpers."""

from typing import Annotated, Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

from shooting_fighter_shared.models.player_state import PlayerState


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PlayerInputPayload(StrictModel):
    forward: bool = False
    backward: bool = False
    left: bool = False
    right: bool = False
    yaw: float = Field(ge=0.0, lt=360.0)


class InputMessage(StrictModel):
    type: Literal["input"]
    sequence: int = Field(ge=1, le=2**31 - 1)
    payload: PlayerInputPayload


class WelcomeMessage(StrictModel):
    type: Literal["welcome"] = "welcome"
    protocol_version: Literal[1] = 1
    player_id: str
    room: str


class SnapshotMessage(StrictModel):
    type: Literal["snapshot"] = "snapshot"
    tick: int = Field(ge=0)
    players: list[PlayerState]


class PlayerJoinedMessage(StrictModel):
    type: Literal["player_joined"] = "player_joined"
    player_id: str


class PlayerLeftMessage(StrictModel):
    type: Literal["player_left"] = "player_left"
    player_id: str


class ErrorMessage(StrictModel):
    type: Literal["error"] = "error"
    code: str
    message: str


ServerMessage: TypeAlias = Annotated[
    WelcomeMessage | SnapshotMessage | PlayerJoinedMessage | PlayerLeftMessage | ErrorMessage,
    Field(discriminator="type"),
]
SERVER_MESSAGE_ADAPTER = TypeAdapter(ServerMessage)


def parse_server_message(data: str | bytes) -> ServerMessage:
    """Validate and parse a server-to-client protocol message."""
    return SERVER_MESSAGE_ADAPTER.validate_json(data)
