"""Load the MIoT specs fetched for the Xiaomi deep tests."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Final

_ROOT: Final = Path(__file__).resolve().parents[3]
_SPECS: Final = _ROOT / "tests" / "xiaomi" / "specs"
_MANIFEST: Final = Path(__file__).resolve().parent / "manifest.json"
FETCHED_ON: Final = "2026-11-04"
SOURCE: Final = "https://miot-spec.org/miot-spec-v2/instance?type="


@dataclass(frozen=True, slots=True)
class SpecRecord:
    """One model's fetched spec and the file the suite reads."""

    model: str
    urn: str
    spec_file: str
    version: int
    fetched_on: str
    source_url: str
    catalog_released: tuple[int, ...]
    canonical_identical: bool
    description_drift: bool
    document: dict[str, object]


def manifest_models() -> dict[str, dict[str, object]]:
    """Return the fetch manifest keyed by model id."""
    loaded = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    models = loaded["models"]
    if not isinstance(models, dict):
        raise TypeError("manifest models")
    return models


def load_record(model: str) -> SpecRecord:
    """Load the spec document selected for one model."""
    raw = manifest_models()[model]
    spec_file = raw["spec_file"]
    urn = raw["urn"]
    version = raw["version"]
    released = raw["catalog_released"]
    identical = raw["canonical_identical"]
    drift = raw["description_drift"]
    if not isinstance(spec_file, str) or not isinstance(urn, str):
        raise TypeError(model)
    if not isinstance(version, int) or not isinstance(released, list):
        raise TypeError(model)
    if not isinstance(identical, bool) or not isinstance(drift, bool):
        raise TypeError(model)
    document = json.loads((_SPECS / spec_file).read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise TypeError(spec_file)
    versions = tuple(item for item in released if isinstance(item, int))
    return SpecRecord(
        model=model,
        urn=urn,
        spec_file=spec_file,
        version=version,
        fetched_on=FETCHED_ON,
        source_url=SOURCE + urn,
        catalog_released=versions,
        canonical_identical=identical,
        description_drift=drift,
        document=document,
    )


def spec_token(urn: str) -> str:
    """Return the property or action name embedded in a MIoT URN."""
    parts = urn.split(":")
    if len(parts) >= 4 and parts[2] in {"property", "action", "event", "service"}:
        return parts[3]
    return ""
