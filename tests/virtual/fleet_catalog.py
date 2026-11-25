"""Every supported Xiaomi model and each published spec version."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Final

from tests.xiaomi.deep.corpus import manifest_models

_SPECS: Final = Path(__file__).resolve().parents[1] / "xiaomi" / "specs"
_REPRESENTATIVE: Final[tuple[tuple[str, str], ...]] = (
    ("station", "xiaomi.vacuum.b108gl"),
    ("sweep", "xiaomi.vacuum.b112"),
    ("essential", "mijia.vacuum.v1"),
    ("robot", "xiaomi.vacuum.ov31gl"),
    ("roller", "xiaomi.vacuum.qv41gl"),
    ("mijia-cn", "xiaomi.vacuum.pv32cn"),
)


@dataclass(frozen=True, slots=True)
class RobotProfile:
    """One model string and the spec file the robot should publish."""

    model: str
    spec_file: str
    submodel: bool

    def document(self) -> dict[str, object]:
        """Load this profile's MIoT document."""
        loaded = json.loads((_SPECS / self.spec_file).read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise TypeError(self.spec_file)
        return loaded


def robot_profiles() -> tuple[RobotProfile, ...]:
    """Return canonical models first, then older spec versions of those models."""
    manifest = manifest_models()
    canonical = [
        RobotProfile(model=model, spec_file=_spec_file(raw), submodel=False)
        for model, raw in sorted(manifest.items())
    ]
    known = {profile.spec_file: profile.model for profile in canonical}
    extras: list[RobotProfile] = []
    for path in sorted(_SPECS.glob("*.json")):
        if path.name in known:
            continue
        parent = _parent_model(path.name, known)
        if parent is None:
            raise KeyError(path.name)
        extras.append(RobotProfile(model=parent, spec_file=path.name, submodel=True))
    return tuple(canonical + extras)


def representative_models() -> tuple[tuple[str, str], ...]:
    """Return one model string for each Xiaomi behavior family."""
    return _REPRESENTATIVE


def _spec_file(raw: dict[str, object]) -> str:
    spec_file = raw.get("spec_file")
    if not isinstance(spec_file, str):
        raise TypeError("spec_file")
    return spec_file


def _parent_model(spec_file: str, known: dict[str, str]) -> str | None:
    stem = spec_file.removesuffix(".json")
    for canonical, model in known.items():
        base = canonical.removesuffix(".json")
        if stem.startswith(base + "_v"):
            return model
    return None
