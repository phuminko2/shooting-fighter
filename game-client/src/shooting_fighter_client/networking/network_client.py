"""Async WebSocket worker with a thread-safe event queue for the renderer."""

import asyncio
import json
import queue
import threading
from typing import Any

import websockets

from shooting_fighter_shared.messages import InputMessage, PlayerInputPayload, parse_server_message


class NetworkClient:
    def __init__(self, url: str) -> None:
        self.url = url
        self.events: queue.SimpleQueue[Any] = queue.SimpleQueue()
        self._inputs: queue.SimpleQueue[PlayerInputPayload] = queue.SimpleQueue()
        self._thread = threading.Thread(target=self._thread_main, daemon=True)
        self._sequence = 0

    def start(self) -> None:
        self._thread.start()

    def submit_input(self, payload: PlayerInputPayload) -> None:
        self._inputs.put(payload)

    def _thread_main(self) -> None:
        asyncio.run(self._run())

    async def _run(self) -> None:
        try:
            async with websockets.connect(self.url, max_size=4096) as websocket:
                self.events.put(("status", "Connected"))
                sender = asyncio.create_task(self._send_inputs(websocket))
                try:
                    async for raw in websocket:
                        try:
                            self.events.put(parse_server_message(raw))
                        except Exception as exc:
                            self.events.put(("error", f"Invalid server message: {exc}"))
                finally:
                    sender.cancel()
                    await asyncio.gather(sender, return_exceptions=True)
        except Exception as exc:
            self.events.put(("status", f"Disconnected: {exc}"))

    async def _send_inputs(self, websocket: Any) -> None:
        while True:
            latest: PlayerInputPayload | None = None
            while True:
                try:
                    latest = self._inputs.get_nowait()
                except queue.Empty:
                    break
            if latest is not None:
                self._sequence += 1
                message = InputMessage(type="input", sequence=self._sequence, payload=latest)
                await websocket.send(message.model_dump_json())
            await asyncio.sleep(0.05)
