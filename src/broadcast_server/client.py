import asyncio
import sys

from websockets.asyncio.client import connect


async def connect_to(url: str, name: str) -> None:
    async with connect(url) as websocket:
        print(f"Connected client with name {name} to server {url}", file=sys.stderr)

        while True:
            try:
                message = input()
            except EOFError:
                print("End of input", file=sys.stderr)
                break

            if message:
                await websocket.send(f"{name}: {message}")

            while True:
                try:
                    async with asyncio.timeout(0.1):
                        response = await websocket.recv()
                except TimeoutError:
                    break

                print(response)
