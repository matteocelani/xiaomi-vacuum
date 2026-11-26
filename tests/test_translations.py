"""Italian and English catalogs cover every key, and Italian is not leftover English."""

from __future__ import annotations

import json
from pathlib import Path
import re

_ROOT = Path("custom_components/xiaomi_robot_vacuum")
_SHARED = frozenset(
    {
        "10 m²",
        "15 m²",
        "20 m²",
        "25 m²",
        "5 m²",
        "8 m²",
        "Area",
        "BSSID",
        "Backup",
        "Base",
        "CleanGenius",
        "Dreame",
        "Dreamehome",
        "India",
        "Material",
        "Menu",
        "Mijia",
        "MOVAhome",
        "Password",
        "RSSI",
        "Router",
        "Russia",
        "SSID",
        "Singapore",
        "Standard",
        "TURBO",
        "TROUVER",
        "Taiwan",
        "Turbo",
        "Url",
        "Volume",
        "Xiaomi Home",
    }
)
_ENGLISH_LEFTOVER = re.compile(
    r"\b(mop|docking|crossing|washboard|bumper|standby|climber|spot|genius|sweep)\b",
    re.IGNORECASE,
)


def _load(name: str) -> dict[str, object]:
    return json.loads((_ROOT / name).read_text(encoding="utf-8"))


def _leaves(node: object, prefix: str = "") -> dict[str, str]:
    found: dict[str, str] = {}
    if isinstance(node, dict):
        for key, value in node.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if isinstance(value, dict):
                found.update(_leaves(value, path))
            elif isinstance(value, str):
                found[path] = value
    return found


def test_every_catalog_key_is_present_in_english_and_italian() -> None:
    """Entity, service, option, and error keys exist in both catalogs."""
    source = _leaves(_load("strings.json"))
    english = _leaves(_load("translations/en.json"))
    italian = _leaves(_load("translations/it.json"))
    assert set(source) == set(english) == set(italian)


def test_identical_italian_strings_are_shared_words() -> None:
    """A copied English sentence is not an Italian translation."""
    english = _leaves(_load("translations/en.json"))
    italian = _leaves(_load("translations/it.json"))
    copied = {
        path: value
        for path, value in english.items()
        if path in italian
        and italian[path] == value
        and any(char.isalpha() for char in value)
    }
    unexpected = {path: value for path, value in copied.items() if value not in _SHARED}
    assert unexpected == {}


def test_italian_dnd_and_stop_labels_are_translated() -> None:
    italian = _load("translations/it.json")
    assert italian["entity"]["switch"]["dnd"]["name"] == "Non disturbare"
    assert (
        italian["entity"]["time"]["dnd_start"]["name"]
        == "Orario di inizio non disturbare"
    )
    assert (
        italian["entity"]["time"]["dnd_end"]["name"] == "Orario di fine non disturbare"
    )
    actions = italian["entity_component"]["frontend_action"]["state"]
    messages = italian["entity_component"]["frontend_message"]["state"]
    assert actions["stop_drying"] == "Ferma asciugatura"
    assert actions["stop_bag_drying"] == "Ferma asciug. sacco"
    assert messages["stop_drying"] == "Fermare l'asciugatura?"
    assert messages["stop_bag_drying"] == "Fermare l'asciugatura del sacco?"


def test_italian_labels_do_not_keep_english_words() -> None:
    """State, service, and error labels are Italian, not leftover English words."""
    italian = _leaves(_load("translations/it.json"))
    leftover = {
        path: value
        for path, value in italian.items()
        if _ENGLISH_LEFTOVER.search(value)
    }
    assert leftover == {}
    assert (
        italian["entity.sensor.obstacle_reason.state.failed_to_cross_threshold"]
        == "Soglia non superata"
    )
    assert (
        italian["entity.sensor.state.state.installing_mop"] == "Installazione del panno"
    )
    assert (
        italian["entity.sensor.state.state.uninstalling_mop"] == "Rimozione del panno"
    )
    assert (
        italian["entity.sensor.state.state.navigating_to_climber"]
        == "Navigazione verso lo scavalcatore"
    )
    assert (
        italian["entity.sensor.task_end_type.state.manual_docking"]
        == "Aggancio manuale"
    )
    assert (
        italian[
            "entity.sensor.task_interrupt_reason.state.mop_pad_fallen_off_crossing_obstacle"
        ]
        == "Mocio caduto superando un ostacolo"
    )
    assert italian["entity.sensor.status.state.standby"] == "In attesa"
    assert italian["entity.sensor.status.state.sleeping"] == "In sospensione"
    assert italian["entity.sensor.error.state.bumper"] == "Paraurti bloccato"
    assert (
        italian["entity.sensor.error.state.mop_pad"]
        == "Asse di lavaggio non installata correttamente."
    )
    assert (
        italian["exceptions.fast_mapping_mop_installed.message"]
        == "Assicurati che il panno non sia installato prima della mappatura rapida"
    )
