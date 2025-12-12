from pathlib import Path
from typing import Any, TypeVar

import json

import msgspec

T = TypeVar("T")

_encoder = msgspec.json.Encoder()
_decoder = msgspec.json.Decoder()


def encode(obj: Any) -> bytes:
    """Encode object to JSON bytes"""
    return _encoder.encode(obj)


def encode_str(obj: Any) -> str:
    """Encode object to JSON string"""
    return _encoder.encode(obj).decode("utf-8")


def decode(data: bytes | str, type_: type[T] | None = None) -> T | Any:
    """Decode JSON data, optionally to a specific type"""
    if isinstance(data, str):
        data = data.encode("utf-8")

    if type_ is None:
        return _decoder.decode(data)

    return msgspec.json.decode(data, type=type_)


def to_builtins(obj: Any) -> Any:
    """Convert msgspec Struct (or any object) to plain Python types"""
    return msgspec.to_builtins(obj)


def load_file(path: Path, type_: type[T] | None = None) -> T | dict | None:
    """Load JSON from file"""
    if not path.exists():
        return None

    try:
        return decode(path.read_bytes(), type_)

    except (msgspec.DecodeError, OSError):
        return None


def save_file(path: Path, data: Any, pretty: bool = False) -> None:
    """Save object as JSON to file"""
    path.parent.mkdir(parents=True, exist_ok=True)

    if pretty:
        # msgspec doesn't support indent, use stdlib for pretty printing
        path.write_text(
            json.dumps(to_builtins(data), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    else:
        path.write_bytes(encode(data))
