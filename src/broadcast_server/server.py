from websockets.asyncio.server import ServerConnection, serve


async def _handler(websocket: ServerConnection) -> None:
    pass


async def start(host: str, port: int) -> None:
    async with serve(_handler, host, port) as server:
        sockets = server.sockets
        port = sockets[0].getsockname()[1]
        print(f"Started a new server at host: {host} and port: {port}...", flush=True)
        await server.serve_forever()
