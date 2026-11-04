"""Model catalog decoding for the current DEVICE_INFO blob."""

from __future__ import annotations

import base64
import gzip
import json

from custom_components.dreame_vacuum.dreame.catalog import (
    catalog_supports_model,
    load_model_catalog,
)
from custom_components.dreame_vacuum.dreame.const import DEVICE_INFO
from custom_components.dreame_vacuum.dreame.exceptions import DeviceException
import pytest


def _blob(records, capabilities, keys, model_index) -> str:
    payload = json.dumps(
        [records, capabilities, keys, model_index], separators=(",", ":")
    ).encode()
    return base64.b64encode(gzip.compress(payload, mtime=0)).decode("ascii")


def test_s20_plus_and_x20_max_load_from_the_current_catalog():
    models = load_model_catalog(DEVICE_INFO)
    assert models["xiaomi.vacuum.b108gl"] == 1
    assert models["xiaomi.vacuum.d109gl"] == 1
    assert models["xiaomi.vacuum.d102gl"] == 1
    assert models["xiaomi.vacuum.ov31gl"] == 1
    assert models["xiaomi.vacuum.ov71gl"] == 1
    assert models["xiaomi.vacuum.ov81gl"] == 1
    assert models["xiaomi.vacuum.ov51gl"] == 1
    assert models["xiaomi.vacuum.e101gb"] == 1
    assert models["xiaomi.vacuum.ov42gl"] == 1
    assert models["xiaomi.vacuum.ov21gl"] == 1
    assert models["xiaomi.vacuum.ov43gb"] == 1
    assert models["xiaomi.vacuum.pv32gl"] == 1
    assert models["xiaomi.vacuum.pv11gl"] == 1
    assert models["xiaomi.vacuum.pv21gl"] == 1
    assert models["xiaomi.vacuum.pv51gl"] == 1
    assert models["xiaomi.vacuum.pv81gl"] == 1
    assert models["xiaomi.vacuum.qv41gl"] == 1
    assert models["xiaomi.vacuum.qv42gl"] == 1
    assert models["xiaomi.vacuum.b112"] == 1
    assert models["xiaomi.vacuum.b112gl"] == 1
    assert models["xiaomi.vacuum.b112bk"] == 1
    assert models["xiaomi.vacuum.c108"] == 1
    assert models["xiaomi.vacuum.d106gl"] == 1
    assert models["xiaomi.vacuum.c101eu"] == 1
    assert models["xiaomi.vacuum.b106eu"] == 1
    assert models["xiaomi.vacuum.b106bk"] == 1
    assert models["xiaomi.vacuum.pv32cn"] == 1
    assert models["xiaomi.vacuum.qv41cn"] == 1
    assert models["xiaomi.vacuum.ov31cn"] == 1
    assert models["xiaomi.vacuum.ov21cn"] == 1
    assert models["xiaomi.vacuum.ov42cn"] == 1
    assert models["xiaomi.vacuum.c101"] == 1
    assert models["xiaomi.vacuum.c103"] == 1
    assert models["xiaomi.vacuum.d102ev"] == 1
    assert models["xiaomi.vacuum.pv11cn"] == 1
    assert models["xiaomi.vacuum.pv21cn"] == 1
    assert models["xiaomi.vacuum.qv12cn"] == 1
    assert models["xiaomi.vacuum.pv31cn"] == 1
    assert models["xiaomi.vacuum.c107"] == 1
    assert models["xiaomi.vacuum.ov81cn"] == 1
    assert models["xiaomi.vacuum.d101"] == 1
    assert models["xiaomi.vacuum.c104"] == 1
    assert models["xiaomi.vacuum.c102gl"] == 1
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.b108gl") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.d109gl") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.d102gl") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.ov31gl") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.ov71gl") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.ov81gl") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.ov51gl") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.e101gb") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.ov42gl") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.ov21gl") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.ov43gb") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.pv32gl") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.pv11gl") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.pv21gl") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.pv51gl") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.pv81gl") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.qv41gl") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.qv42gl") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.b112") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.b112gl") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.b112bk") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.c108") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.d106gl") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.c101eu") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.b106eu") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.b106bk") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.pv32cn") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.qv41cn") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.ov31cn") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.ov21cn") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.ov42cn") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.c101") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.c103") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.d102ev") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.pv11cn") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.pv21cn") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.qv12cn") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.pv31cn") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.c107") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.ov81cn") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.d101") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.c104") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.c102gl") is True
    assert catalog_supports_model(DEVICE_INFO, "xiaomi.vacuum.notreal") is False


def test_catalog_prefixes_follow_the_brand_code():
    blob = _blob(
        [[0, 4, 0], [1, 5, 0], [2, 6, 0], [3, 7, 0], [], [9, "no"]],
        [[[1, 1]]],
        ["key"],
        {"dreame": 0, "mijia": 1, "mova": 2, "trouver": 3, "empty": 4, "badflag": 5},
    )
    models = load_model_catalog(blob)
    assert models == {
        "dreame.vacuum.dreame": 4,
        "xiaomi.vacuum.mijia": 5,
        "mova.vacuum.mova": 6,
        "trouver.vacuum.trouver": 7,
    }


def _encoded(value: object) -> str:
    payload = json.dumps(value, separators=(",", ":")).encode()
    return base64.b64encode(gzip.compress(payload, mtime=0)).decode("ascii")


def test_catalog_rejects_records_capability_load_would_reject():
    capability = [[1, 1]]
    accepted = _blob([[1, 1, 0, 0]], [capability], ["secret"], {"ok": 0})
    assert catalog_supports_model(accepted, "xiaomi.vacuum.ok") is True
    no_key = _blob([[1, 1, 0]], [capability], ["secret"], {"short": 0})
    assert catalog_supports_model(no_key, "xiaomi.vacuum.short") is True
    assert catalog_supports_model(accepted, "xiaomi.vacuum.missing") is False
    assert catalog_supports_model(_encoded([capability]), "xiaomi.vacuum.ok") is False
    assert (
        catalog_supports_model(_encoded(["records", [], [], {"ok": 0}]), "x") is False
    )
    rejected = (
        _blob([[1, 1, 0, 0]], [capability], ["secret"], {"bad": 3}),
        _blob([[1, 1, 0, 0]], [capability], ["secret"], {"bad": "0"}),
        _blob([[1, 1]], [capability], ["secret"], {"bad": 0}),
        _blob(["nope"], [capability], ["secret"], {"bad": 0}),
        _blob([[1, 1, -1, 0]], [capability], ["secret"], {"bad": 0}),
        _blob([[1, 1, 0, 0]], [None], ["secret"], {"bad": 0}),
        _blob([[1, 1, 0, "x"]], [capability], ["secret"], {"bad": 0}),
        _blob([[1, 1, 0, 0]], [capability], [""], {"bad": 0}),
        _blob([[1, 1, 0, 1]], [capability], ["secret", "extra"], {"bad": 0}),
        _blob([[1, 1, 0, 1]], [capability, capability], ["secret"], {"bad": 0}),
        _blob([[1, 1, 0, 0]], [], ["secret"], {"bad": 0}),
    )
    for blob in rejected:
        assert catalog_supports_model(blob, "xiaomi.vacuum.bad") is False
    skipped = _blob(
        [[1, 1, 0], [], [1, "flag", 0]],
        [capability],
        ["secret"],
        {"good": 0, "empty": 1, "text": "1", "high": 9, "flag": 2},
    )
    assert load_model_catalog(skipped) == {"xiaomi.vacuum.good": 1}
    with pytest.raises(DeviceException):
        load_model_catalog(_encoded([[], [], [], []]))


def test_catalog_rejects_a_blob_that_is_not_a_list():
    payload = base64.b64encode(gzip.compress(b"{}", mtime=0)).decode("ascii")
    with pytest.raises(DeviceException):
        load_model_catalog(payload)
    with pytest.raises(DeviceException):
        catalog_supports_model(payload, "xiaomi.vacuum.b108gl")
