"""Config for the second-brain <-> life-os sync bridge.

Loads env in this order:
  1. ~/.config/sho-brain/secrets.env  (user convention, per reference_secondbrain.md)
  2. ~/.config/obsidian-second-brain/.env  (skill default)
  3. process environment (CI/manual override always wins)

Required:
  LIFEOS_BASE_URL        e.g. https://sho.johanvillalba.com or http://127.0.0.1:8000
  LIFEOS_SERVICE_TOKEN   matches SYNC_SERVICE_TOKEN in life-os .env

Optional:
  OBSIDIAN_VAULT_PATH    defaults to ~/Documents/Sho
  LIFEOS_REQUEST_TIMEOUT defaults to 15 (seconds)
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Order matters: later loads do NOT override earlier ones (override=False default),
# so sho-brain wins over the skill default, and the live os.environ wins over both.
_CONFIG_FILES = [
    Path.home() / ".config" / "sho-brain" / "secrets.env",
    Path.home() / ".config" / "obsidian-second-brain" / ".env",
]
for _path in _CONFIG_FILES:
    if _path.exists():
        load_dotenv(_path, override=False)


class ConfigError(SystemExit):
    """Raised when required sync config is missing."""


def _required(name: str) -> str:
    val = (os.environ.get(name) or "").strip()
    if not val:
        raise ConfigError(
            f"\n{name} not configured.\n"
            f"Add it to one of:\n"
            f"  {_CONFIG_FILES[0]}\n"
            f"  {_CONFIG_FILES[1]}\n"
        )
    return val


def _optional(name: str, default: str = "") -> str:
    return (os.environ.get(name) or "").strip() or default


def lifeos_base_url() -> str:
    """Strip trailing slash; the client always builds /api/<path> URLs."""
    return _required("LIFEOS_BASE_URL").rstrip("/")


def lifeos_service_token() -> str:
    return _required("LIFEOS_SERVICE_TOKEN")


def vault_path() -> Path:
    raw = _optional("OBSIDIAN_VAULT_PATH", str(Path.home() / "Documents" / "Sho"))
    path = Path(raw).expanduser()
    if not path.is_dir():
        raise ConfigError(
            f"\nOBSIDIAN_VAULT_PATH does not exist or is not a directory: {path}\n"
            f"Set OBSIDIAN_VAULT_PATH in your secrets.env to override.\n"
        )
    return path


def request_timeout() -> int:
    try:
        return int(_optional("LIFEOS_REQUEST_TIMEOUT", "15"))
    except ValueError:
        return 15
