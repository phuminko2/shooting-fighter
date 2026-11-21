from shooting_fighter_shared.messages import InputMessage, PlayerInputPayload
from shooting_fighter_server.rooms.room import Room


def test_room_join_leave_and_capacity() -> None:
    room = Room(max_players=1)
    player = room.join(object())
    assert player.player_id in room.players
    try:
        room.join(object())
    except ValueError:
        pass
    else:
        raise AssertionError("full room should reject another player")
    assert room.leave(player.player_id)
    assert not room.leave(player.player_id)


def test_input_sequence_and_movement_bounds() -> None:
    room = Room()
    player = room.join(object())
    input_message = InputMessage(
        type="input",
        sequence=1,
        payload=PlayerInputPayload(forward=True, yaw=0),
    )
    assert room.accept_input(player.player_id, input_message)
    assert not room.accept_input(player.player_id, input_message)
    room.step()
    assert player.z > 0
