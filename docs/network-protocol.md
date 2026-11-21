# Protocol v1

Messages are UTF-8 JSON objects over WebSocket at `/ws`. The server assigns a player ID and automatically joins the single `battle` room. Client input is validated and only the latest increasing sequence number is accepted. The server computes positions and broadcasts snapshots; clients never submit positions.

Client input:

```json
{"type":"input","sequence":1,"payload":{"forward":true,"backward":false,"left":false,"right":false,"yaw":90.0}}
```

Server messages are `welcome`, `snapshot`, `player_joined`, `player_left`, and `error`. Snapshot players contain `id`, `x`, `y`, `z`, and `yaw`. Input messages are limited to 4096 UTF-8 bytes.

Coordinates are Y-up, player origin is at the center of the 2-unit-tall body (`y=1` at spawn), and yaw is degrees modulo 360 with 0 facing +Z and positive yaw turning toward +X. X/Z movement is bounded to `[-20, 20]` at 5 units/second. The server ticks at 20 Hz and sends snapshots at 10 Hz.
