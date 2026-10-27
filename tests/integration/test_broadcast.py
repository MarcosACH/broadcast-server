import asyncio

from websockets.asyncio.client import connect


async def test_message_reaches_others_but_not_sender(server_url: str) -> None:
    async with connect(server_url) as a, connect(server_url) as b:
        await a.send("hello")
        async with asyncio.timeout(2):
            assert await b.recv() == "hello"

        await b.send("pong")
        async with asyncio.timeout(2):
            assert await a.recv() == "pong"
