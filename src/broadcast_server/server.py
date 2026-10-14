from websockets.asyncio.server import ServerConnection, serve


async def _handler(websocket: ServerConnection) -> None:
    print("Connected...", flush=True)
    async for message in websocket:
        print("got", message, flush=True)
    print("Connection ended", flush=True)


async def start(host: str, port: int) -> None:
    async with serve(_handler, host, port) as server:
        sockets = server.sockets
        port = sockets[0].getsockname()[1]
        print(f"Started a new server at host: {host} and port: {port}...", flush=True)
        await server.serve_forever()
