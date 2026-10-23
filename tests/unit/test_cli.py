from argparse import ArgumentTypeError

import pytest
from websockets.exceptions import ConnectionClosed, InvalidHandshake

import broadcast_server.cli
from broadcast_server.cli import build_parser, main, parse_port, parse_url


def test_start_defaults() -> None:
    parser = build_parser()
    args = parser.parse_args(["start"])
    assert args.host == "localhost"
    assert args.port == 9000


def test_connect_defaults() -> None:
    parser = build_parser()
    args = parser.parse_args(["connect", "--name", "test"])
    assert args.url == "ws://localhost:9000"


def test_start_parses_port_as_int() -> None:
    parser = build_parser()
    args = parser.parse_args(["start", "--port", "8080"])
    assert isinstance(args.port, int)
    assert args.port == 8080


def test_start_edge_ports_are_accepted() -> None:
    parser = build_parser()
    min_port = parser.parse_args(["start", "--port", "0"])
    max_port = parser.parse_args(["start", "--port", "65535"])

    assert min_port.port == 0
    assert max_port.port == 65535


@pytest.mark.parametrize(("value", "expected"), [("0", 0), ("8080", 8080), ("65535", 65535)])
def test_parse_port_accepts_valid_values(value: str, expected: int) -> None:
    assert parse_port(value) == expected


@pytest.mark.parametrize(
    ("bad", "err_message"),
    [
        ("abc", "is not a valid integer port"),
        ("-1", "is out of bounds"),
        ("65536", "is out of bounds"),
    ],
)
def test_parse_port_rejects_invalid_values(bad: str, err_message: str) -> None:
    with pytest.raises(ArgumentTypeError, match=err_message):
        parse_port(bad)


@pytest.mark.parametrize("bad", ["abc", "-1", "65536"])
def test_start_bad_ports_through_the_parser(bad: str, capsys: pytest.CaptureFixture[str]) -> None:
    parser = build_parser()
    with pytest.raises(SystemExit) as excinfo:
        parser.parse_args(["start", "--port", bad])
    assert excinfo.value.code == 2
    out, err = capsys.readouterr()
    assert out == ""
    assert "argument --port" in err


def test_no_subcommand_exits_with_2(capsys: pytest.CaptureFixture[str]) -> None:
    parser = build_parser()
    with pytest.raises(SystemExit) as excinfo:
        parser.parse_args([])
    assert excinfo.value.code == 2
    out, err = capsys.readouterr()
    assert out == ""
    assert "the following arguments are required" in err


def test_connect_without_name(capsys: pytest.CaptureFixture[str]) -> None:
    parser = build_parser()
    with pytest.raises(SystemExit) as excinfo:
        parser.parse_args(["connect"])
    assert excinfo.value.code == 2
    out, err = capsys.readouterr()
    assert out == ""
    assert "--name" in err


def test_help_command_exits_with_zero(capsys: pytest.CaptureFixture[str]) -> None:
    parser = build_parser()
    with pytest.raises(SystemExit) as excinfo:
        parser.parse_args(["--help"])
    assert excinfo.value.code == 0
    out, err = capsys.readouterr()
    assert "start" in out
    assert "connect" in out
    assert err == ""


def test_main_with_start(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, int]] = []

    async def fake_start(host: str, port: int) -> None:
        calls.append((host, port))

    monkeypatch.setattr(broadcast_server.cli, "start", fake_start)

    assert main(["start", "--port", "8080"]) == 0
    assert calls == [("localhost", 8080)]


def test_main_with_connect(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    calls: list[tuple[str, str]] = []

    async def fake_connect_to(url: str, name: str) -> None:
        calls.append((url, name))

    monkeypatch.setattr(broadcast_server.cli, "connect_to", fake_connect_to)

    assert main(["connect", "--name", "marcos"]) == 0
    assert calls == [("ws://localhost:9000", "marcos")]
    out, err = capsys.readouterr()
    assert out == ""
    assert err == ""


def test_main_with_start_and_keyboard_interrupt(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    async def fake_start(host: str, port: int) -> None:
        raise KeyboardInterrupt

    monkeypatch.setattr(broadcast_server.cli, "start", fake_start)

    assert main(["start", "--port", "8080"]) == 0
    out, err = capsys.readouterr()
    assert "Server stopped" in out
    assert err == ""


@pytest.mark.parametrize(
    "value",
    [
        "ws://localhost:9000",
        "wss://example.com",
        "wss://pepe/chat",
        "ws://[::1]:9000",
    ],
)
def test_parse_url_accepts_valid_values(value: str) -> None:
    assert parse_url(value) == value


@pytest.mark.parametrize(
    ("bad", "err_message"),
    [
        ("http://localhost:9000", "must start with"),
        ("ws://:9000", "no host"),
        ("ws://localhost:99999", "not a valid URL"),
        ("ws://localhost:0", "port 0"),
    ],
)
def test_parse_url_rejects_invalid_values(bad: str, err_message: str) -> None:
    with pytest.raises(ArgumentTypeError, match=err_message):
        parse_url(bad)


def test_connect_bad_scheme_through_the_parser(capsys: pytest.CaptureFixture[str]) -> None:
    parser = build_parser()
    with pytest.raises(SystemExit) as excinfo:
        parser.parse_args(["connect", "--url", "http://"])
    assert excinfo.value.code == 2
    out, err = capsys.readouterr()
    assert out == ""
    assert "argument --url" in err


@pytest.mark.parametrize(
    ("error", "expected_code", "expected_message"),
    [
        pytest.param(OSError(), 1, "Unable to connect", id="os_error"),
        pytest.param(ConnectionClosed(None, None), 1, "Server disconnected", id="disconnected"),
        pytest.param(InvalidHandshake(), 1, "Not a WebSocket server", id="invalid_ws_server"),
        pytest.param(KeyboardInterrupt(), 0, "Client stopped", id="ctrl-c"),
    ],
)
def test_main_with_connect_error_paths(
    error: BaseException,
    expected_code: int,
    expected_message: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    async def fake_connect_to(url: str, name: str) -> None:
        raise error

    monkeypatch.setattr(broadcast_server.cli, "connect_to", fake_connect_to)

    assert main(["connect", "--name", "marcos"]) == expected_code
    out, err = capsys.readouterr()
    assert out == ""
    assert expected_message in err
