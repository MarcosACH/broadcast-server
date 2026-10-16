import argparse
import asyncio
from collections.abc import Sequence

from broadcast_server.client import connect_to
from broadcast_server.server import start

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 9000


def parse_port(value: str) -> int:
    try:
        port = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid integer port.") from None

    if not (0 <= port <= 65535):
        raise argparse.ArgumentTypeError(f"Port {port} is out of bounds (must be 0-65535).")

    return port


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="broadcast-server", description="Broadcast Server CLI")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available subcommands")

    parser_start = subparsers.add_parser("start", help="Start a new broadcast server")
    parser_start.set_defaults(func=_start_handler)
    parser_start.add_argument("--host", default=DEFAULT_HOST)
    parser_start.add_argument("--port", type=parse_port, default=DEFAULT_PORT)

    parser_connect = subparsers.add_parser("connect", help="Connect to a broadcast server")
    parser_connect.set_defaults(func=_connect_handler)
    parser_connect.add_argument("--url", default=f"ws://{DEFAULT_HOST}:{DEFAULT_PORT}")
    parser_connect.add_argument("--name", required=True)

    return parser


def _start_handler(args: argparse.Namespace) -> int:
    host = args.host
    port = args.port

    try:
        asyncio.run(start(host, port))
    except KeyboardInterrupt:
        print("Server stopped")
    return 0


def _connect_handler(args: argparse.Namespace) -> int:
    url = args.url
    name = args.name

    asyncio.run(connect_to(url, name))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    return int(args.func(args))
