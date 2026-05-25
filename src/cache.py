"""Persistent JSON cache for fetched outbreak data."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

_CACHE_DIR = Path(__file__).parent.parent / "data" / "cache"


def _path(name: str) -> Path:
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return _CACHE_DIR / f"{name}.json"


def load(name: str) -> tuple[list[dict], str | None]:
    """Load cached records. Returns (records, timestamp_str) or ([], None) on miss."""
    p = _path(name)
    if not p.exists():
        return [], None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data.get("records", []), data.get("timestamp")
    except Exception as e:
        logger.warning("Cache load failed for %s: %s", name, e)
        return [], None


def save(name: str, records: list[dict]) -> str:
    """Persist records and return a UTC timestamp string."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    p = _path(name)
    try:
        p.write_text(
            json.dumps({"timestamp": timestamp, "records": records}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        logger.error("Cache save failed for %s: %s", name, e)
    return timestamp
