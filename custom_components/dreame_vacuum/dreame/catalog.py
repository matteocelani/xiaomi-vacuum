"""Decode the vacuum model catalog stored in DEVICE_INFO."""

from __future__ import annotations

import base64
import json
from typing import Final
import zlib

from .exceptions import DeviceException

_GZIP_WINDOW_BITS: Final = zlib.MAX_WBITS | 32
_BRAND_XIAOMI: Final = 1
_BRAND_MOVA: Final = 2
_BRAND_TROUVER: Final = 3
_BRAND_MIJIA: Final = 4
_PREFIX_XIAOMI: Final = "xiaomi"
_PREFIX_MOVA: Final = "mova"
_PREFIX_TROUVER: Final = "trouver"
_PREFIX_DREAME: Final = "dreame"
_PREFIX_MIJIA: Final = "mijia"
# Equality, not a dict lookup, so 1.0 and True still match brand 1.
_BRAND_PREFIXES: Final[tuple[tuple[int, str], ...]] = (
    (_BRAND_XIAOMI, _PREFIX_XIAOMI),
    (_BRAND_MOVA, _PREFIX_MOVA),
    (_BRAND_TROUVER, _PREFIX_TROUVER),
    (_BRAND_MIJIA, _PREFIX_MIJIA),
)
_RECORD_LENGTHS: Final = frozenset({3, 4})


def load_model_catalog(blob: str) -> dict[str, int]:
    """Return model id to catalog flag, using the same brand prefixes as the flow."""
    device_info = _decode_catalog(blob)
    records = device_info[0]
    model_index = device_info[3]
    if not isinstance(records, list) or not isinstance(model_index, dict):
        raise DeviceException("device catalog is missing a section")
    models: dict[str, int] = {}
    for code, record_index in model_index.items():
        if not isinstance(record_index, int):
            continue
        if record_index < 0 or record_index >= len(records):
            continue
        info = records[record_index]
        if not info or not isinstance(info, list) or len(info) < 2:
            continue
        flag = info[1]
        if not isinstance(flag, int):
            continue
        models[_model_id(info[0], code)] = flag
    return models


def catalog_supports_model(blob: str, model: str) -> bool:
    """Return whether capability loading would accept this model id.

    The key-index limit matches capability.load: len(capabilities or key < 0)
    is the capability-list length when that list is non-empty.
    """
    device_info = _decode_catalog(blob)
    if len(device_info) < 4:
        return False
    records = device_info[0]
    capabilities = device_info[1]
    keys = device_info[2]
    model_index = device_info[3]
    if (
        not isinstance(records, list)
        or not isinstance(capabilities, list)
        or not isinstance(keys, list)
        or not isinstance(model_index, dict)
    ):
        return False
    code = model[(model.rfind(".") + 1) :]
    if code not in model_index:
        return False
    record_index = model_index[code]
    if (
        not isinstance(record_index, int)
        or record_index < 0
        or record_index >= len(records)
    ):
        return False
    device = records[record_index]
    if (
        not isinstance(device, list)
        or len(device) not in _RECORD_LENGTHS
        or not isinstance(device[2], int)
        or device[2] < 0
        or device[2] >= len(capabilities)
        or capabilities[device[2]] is None
    ):
        return False
    if len(device) == 4:
        if not isinstance(device[3], int):
            return False
        key_limit_source = capabilities or device[3] < 0
        if (
            device[3] < 0
            or device[3] >= len(key_limit_source)
            or device[3] >= len(keys)
        ):
            return False
        key = keys[device[3]]
        if not isinstance(key, str) or len(key) < 1:
            return False
    return True


def _decode_catalog(blob: str) -> list[object]:
    decoded = json.loads(zlib.decompress(base64.b64decode(blob), _GZIP_WINDOW_BITS))
    if isinstance(decoded, list):
        return decoded
    raise DeviceException("device catalog is not a list")


def _model_id(brand: object, code: object) -> str:
    prefix = _PREFIX_DREAME
    for brand_code, brand_prefix in _BRAND_PREFIXES:
        if brand == brand_code:
            prefix = brand_prefix
            break
    return f"{prefix}.vacuum.{code}"
