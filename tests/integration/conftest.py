from collections.abc import AsyncIterator

import pytest

from broadcast_server.server import create_server


@pytest.fixture
async def server_url() -> AsyncIterator[str]:
    async with create_server("127.0.0.1", 0) as server:
        sockets = server.sockets
        bound_port = sockets[0].getsockname()[1]
        url = f"ws://127.0.0.1:{bound_port}"
        yield url
