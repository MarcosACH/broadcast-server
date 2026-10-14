from websockets.asyncio.server import ServerConnection, serve

connections: set[ServerConnection] = set()


async def _handler(websocket: ServerConnection) -> None:
    print("Connected...", flush=True)
    connections.add(websocket)
    print(f"Active connections: {len(connections)}", flush=True)
    try:
        async for message in websocket:
            print("got", message, flush=True)
    finally:
        print("Connection ended", flush=True)
        connections.remove(websocket)
        print(f"Active connections: {len(connections)}", flush=True)


async def start(host: str, port: int) -> None:
    async with serve(_handler, host, port) as server:
        sockets = server.sockets
        port = sockets[0].getsockname()[1]
        print(f"Started a new server at host: {host} and port: {port}...", flush=True)
        await server.serve_forever()
