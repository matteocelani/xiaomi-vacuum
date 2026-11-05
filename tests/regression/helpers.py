"""Load the inherited Dreame tree and the golden snapshots for regression tests."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from io import BytesIO
import json
import os
from pathlib import Path
import re
import subprocess
import tarfile
from typing import Final
import zlib

REPO_ROOT: Final = Path(__file__).resolve().parents[2]
UPSTREAM_SHA: Final = "f5b8472b8e2e4bb3dff7bc2a81a5fd594eca9585"
_SNAPSHOT_SCRIPT: Final = Path(__file__).resolve().parent / "snapshot_dreame.py"
_DEVICE_INFO: Final = re.compile(r'DEVICE_INFO:\s*Final\s*=\s*\(?\s*"([^"]+)"')


def upstream_root() -> Path:
    """Return a checkout of the Dreame package this fork inherited."""
    root = (
        Path(os.environ.get("TMPDIR", "/tmp")) / f"dreame-upstream-{UPSTREAM_SHA[:12]}"
    )
    marker = root / "custom_components" / "dreame_vacuum" / "dreame" / "const.py"
    if marker.is_file():
        return root
    archive = subprocess.check_output(
        ["git", "archive", UPSTREAM_SHA, "custom_components/dreame_vacuum"],
        cwd=REPO_ROOT,
    )
    root.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=BytesIO(archive)) as bundle:
        bundle.extractall(root)
    return root


def historical_model_id(brand: object, code: object) -> str:
    """Return the pre-catalog model id, where 1.0 and True still mean xiaomi."""
    if brand == 1:
        prefix = "xiaomi"
    elif brand == 2:
        prefix = "mova"
    elif brand == 3:
        prefix = "trouver"
    else:
        prefix = "dreame"
    return f"{prefix}.vacuum.{code}"


def decode_device_info(blob: str) -> list[object]:
    """Return the decoded DEVICE_INFO list."""
    decoded = json.loads(zlib.decompress(base64.b64decode(blob), zlib.MAX_WBITS | 32))
    if isinstance(decoded, list):
        return decoded
    raise TypeError("device catalog is not a list")


def device_info_blob(const_source: str) -> str:
    """Return the DEVICE_INFO literal from a const module source."""
    matched = _DEVICE_INFO.search(const_source)
    if matched is None:
        raise ValueError("DEVICE_INFO literal is missing")
    return matched.group(1)


def original_model_ids() -> list[str]:
    """Return every model id in the inherited catalog, using the old brand prefixes."""
    const_path = (
        upstream_root() / "custom_components" / "dreame_vacuum" / "dreame" / "const.py"
    )
    decoded = decode_device_info(
        device_info_blob(const_path.read_text(encoding="utf-8"))
    )
    records = decoded[0]
    model_index = decoded[3]
    if not isinstance(records, list) or not isinstance(model_index, dict):
        raise TypeError("device catalog is missing a section")
    model_ids: list[str] = []
    for code, record_index in model_index.items():
        if not isinstance(record_index, int) or not 0 <= record_index < len(records):
            continue
        record = records[record_index]
        brand = record[0] if isinstance(record, list) and record else None
        model_ids.append(historical_model_id(brand, code))
    model_ids.sort()
    return model_ids


@dataclass(frozen=True, slots=True)
class RegressionSnapshots:
    """Golden behavior of the fork and of the inherited upstream tree."""

    fork: dict[str, object]
    upstream: dict[str, object]

    def fork_model(self, model_id: str) -> dict[str, object]:
        """Return the fork snapshot for one inherited model id."""
        return _model(self.fork, model_id)

    def upstream_model(self, model_id: str) -> dict[str, object]:
        """Return the upstream snapshot for one inherited model id."""
        return _model(self.upstream, model_id)


def load_snapshots() -> RegressionSnapshots:
    """Run the behavior snapshot against this tree and the inherited tree."""
    return RegressionSnapshots(
        fork=_snapshot(REPO_ROOT),
        upstream=_snapshot(upstream_root()),
    )


def _model(snapshot: dict[str, object], model_id: str) -> dict[str, object]:
    models = snapshot["models"]
    if not isinstance(models, dict):
        raise TypeError("snapshot models are missing")
    model = models[model_id]
    if not isinstance(model, dict):
        raise TypeError("snapshot model is missing")
    return model


def _snapshot(root: Path) -> dict[str, object]:
    output = (
        Path(os.environ.get("TMPDIR", "/tmp")) / f"dreame-snapshot-{root.name}.json"
    )
    completed = subprocess.run(
        [
            "python3",
            str(_SNAPSHOT_SCRIPT),
            "--root",
            str(root),
            "--output",
            str(output),
        ],
        cwd=root,
        env={
            **os.environ,
            "PYTHONPATH": str(root),
            "PYTHONDONTWRITEBYTECODE": "1",
        },
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0 or not output.is_file():
        detail = (completed.stderr or completed.stdout)[-4000:]
        raise RuntimeError(f"snapshot failed for {root}: {detail}")
    loaded = json.loads(output.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise TypeError("snapshot is not an object")
    return loaded
