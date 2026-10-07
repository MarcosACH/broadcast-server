import subprocess
import sysconfig
from pathlib import Path


def test_installed_command_shows_help() -> None:
    scripts = Path(sysconfig.get_path("scripts"))  # the venv's bin/ folder
    result = subprocess.run(
        [scripts / "broadcast-server", "--help"], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0
    assert "usage: broadcast-server" in result.stdout
