import sys

from websockets.asyncio.client import connect


async def connect_to(url: str, name: str) -> None:
    async with connect(url):
        print(f"Connected client with name {name} to server {url}", file=sys.stderr)
