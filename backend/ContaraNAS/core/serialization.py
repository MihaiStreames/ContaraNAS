import json
from pathlib import Path
from typing import Any
from typing import TypeVar

import msgspec


T = TypeVar("T")

_msgpack_encoder = msgspec.msgpack.Encoder()
_msgpack_decoder = msgspec.msgpack.Decoder()

_json_encoder = msgspec.json.Encoder()
_json_decoder = msgspec.json.Decoder()


def encode(obj: Any) -> bytes:
    """Encode object to MessagePack bytes"""
    return _msgpack_encoder.encode(obj)


def encode_str(obj: Any) -> str:
    """Encode object to JSON string"""
    return _json_encoder.encode(obj).decode("utf-8")


def decode[T](data: bytes | str, type_: type[T] | None = None) -> T | Any:
    """Decode MessagePack/JSON data, optionally to a specific type"""
    if isinstance(data, str):
        data = data.encode("utf-8")

    if type_ is None:
        return _msgpack_decoder.decode(data)

    return msgspec.msgpack.decode(data, type=type_)


def to_builtins(obj: Any) -> Any:
    """Convert msgspec Struct (or any object) to plain Python types"""
    return msgspec.to_builtins(obj)


def load_file[T](path: Path, type_: type[T] | None = None) -> T | dict | None:
    """Load JSON from file"""
    if not path.exists():
        return None

    try:
        data = path.read_bytes()
        # files use JSON format for readability
        if type_ is None:
            return _json_decoder.decode(data)
        return msgspec.json.decode(data, type=type_)

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
        # files use JSON format for readability
        path.write_bytes(_json_encoder.encode(data))
