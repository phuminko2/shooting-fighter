import pytest
from pydantic import ValidationError

from shooting_fighter_shared.messages import InputMessage, parse_server_message


def test_input_message_serializes_and_validates() -> None:
    message = InputMessage.model_validate(
        {
            "type": "input",
            "sequence": 1,
            "payload": {"forward": True, "yaw": 90},
        }
    )
    assert InputMessage.model_validate_json(message.model_dump_json()) == message


def test_input_rejects_unknown_fields_and_invalid_sequence() -> None:
    with pytest.raises(ValidationError):
        InputMessage.model_validate(
            {"type": "input", "sequence": 0, "payload": {"yaw": 0}}
        )


def test_parse_server_snapshot() -> None:
    message = parse_server_message(
        '{"type":"snapshot","tick":2,"players":[{"id":"p1","x":0,"y":1,"z":0,"yaw":0}]}'
    )
    assert message.type == "snapshot"
    assert message.players[0].id == "p1"
