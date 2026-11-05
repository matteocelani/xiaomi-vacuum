"""Shared Dreame device behavior stays aligned with the inherited tree."""

from __future__ import annotations

_DREAME_FLAG_TOKENS = ("none", "false", "true", "0", "1", "2", "0.0", "0.5")
_PAUSED_STRING_DIFFERENCES = {
    '"0"': (False, True),
    '"1"': (True, True),
    '"2"': (False, True),
    '"no"': (False, True),
    '""': (False, False),
}
_POSITIVE_STRING_DIFFERENCES = {
    "none": (False, "error:TypeError"),
    '"0"': (False, "error:TypeError"),
    '"1"': (True, "error:TypeError"),
    '"2"': (True, "error:TypeError"),
    '"no"': (True, "error:TypeError"),
    '""': (False, "error:TypeError"),
}
_PARSER_STRINGS = (
    "schedule_string",
    "dnd_string",
    "stream_string",
    "off_peak_string",
)
_PARSER_NUMBERS = (
    "schedule_number",
    "dnd_number",
    "stream_number",
    "off_peak_number",
)


def test_dreame_maps_faults_and_numeric_behavior_match_upstream(
    regression_snapshots: object,
) -> None:
    """Property maps, fault names, and numeric device reads are unchanged."""
    fork = regression_snapshots.fork["device"]
    upstream = regression_snapshots.upstream["device"]
    assert fork["property_enum"] == upstream["property_enum"]
    assert fork["action_enum"] == [*upstream["action_enum"], "RESUME"]
    assert "RESUME" not in fork["action_mapping"]
    assert fork["property_mapping"] == upstream["property_mapping"]
    assert fork["action_mapping"] == upstream["action_mapping"]
    assert fork["did"] == upstream["did"]
    assert fork["error_names"] == upstream["error_names"]
    assert fork["error_name_path"] == upstream["error_name_path"]
    assert fork["group_values"] == upstream["group_values"]
    assert fork["map_actions"] == upstream["map_actions"]
    assert fork["miio_timeout"] == upstream["miio_timeout"] == 2
    assert fork["property_transport"] is None
    assert upstream["property_transport"] is None
    for token in _DREAME_FLAG_TOKENS:
        assert fork["cleaning_paused"][token] == upstream["cleaning_paused"][token]
        if token == "none":
            continue
        assert fork["positive_flags"][token] == upstream["positive_flags"][token]
    for name in _PARSER_STRINGS:
        assert fork["parsers"][name] == upstream["parsers"][name]


def test_non_string_guards_do_not_change_dreame_numeric_results(
    regression_snapshots: object,
) -> None:
    """Stringly MIoT values are guarded. Integers and Dreame JSON strings are not."""
    fork = regression_snapshots.fork["device"]
    upstream = regression_snapshots.upstream["device"]
    for token, (fork_value, upstream_value) in _PAUSED_STRING_DIFFERENCES.items():
        assert fork["cleaning_paused"][token] == fork_value
        assert upstream["cleaning_paused"][token] == upstream_value
    for token, (fork_value, upstream_value) in _POSITIVE_STRING_DIFFERENCES.items():
        assert fork["positive_flags"][token] == fork_value
        assert upstream["positive_flags"][token] == upstream_value
    for name in _PARSER_NUMBERS:
        assert "error" not in fork["parsers"][name]
        assert upstream["parsers"][name]["error"]
