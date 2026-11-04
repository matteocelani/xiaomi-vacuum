"""Xiaomi model identity and value conversion."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from custom_components.dreame_vacuum.dreame.types import (
    DreameVacuumAction,
    DreameVacuumProperty,
    DreameVacuumState,
    DreameVacuumTaskStatus,
)
from custom_components.dreame_vacuum.xiaomi import (
    MODEL_H50,
    MODEL_H50_PRO,
    MODEL_H50_PRO_ROLLER,
    MODEL_H50_ROLLER,
    MODEL_MIJIA_3C,
    MODEL_MIJIA_5_PRO,
    MODEL_MIJIA_5C,
    MODEL_MIJIA_6_MAX,
    MODEL_MIJIA_6_PRO,
    MODEL_MIJIA_7_MAX,
    MODEL_MIJIA_7C,
    MODEL_MIJIA_H40,
    MODEL_MIJIA_M30,
    MODEL_MIJIA_M30_PRO,
    MODEL_MIJIA_M40_S,
    MODEL_MIJIA_ROBOT_VACUUM_4,
    MODEL_MIJIA_ROBOT_VACUUM_5,
    MODEL_MIJIA_ROBOT_VACUUM_6,
    MODEL_MIJIA_SWEEP_MOP_2,
    MODEL_MIJIA_SWEEP_MOP_3,
    MODEL_ROBOT_VACUUM_5_PRO,
    MODEL_ROBOT_VACUUM_6,
    MODEL_ROBOT_VACUUM_6_MAX,
    MODEL_ROBOT_VACUUM_6_PRO,
    MODEL_S20,
    MODEL_S60,
    MODEL_S60_PLUS,
    MODEL_X20,
    MODEL_X20_PRO,
    control_keys,
    controls_of,
    resolve_family,
)
from custom_components.dreame_vacuum.xiaomi.c101eu import X20 as X20_RECORD
from custom_components.dreame_vacuum.xiaomi.d102ev import MIJIA_M30 as M30_RECORD
from custom_components.dreame_vacuum.xiaomi.d102gl import X20_PRO as X20_PRO_RECORD
from custom_components.dreame_vacuum.xiaomi.d106gl import S20 as S20_RECORD
from custom_components.dreame_vacuum.xiaomi.mapping import (
    MODEL_H40,
    MODEL_ROBOT_VACUUM_5,
    MODEL_S20_PLUS,
    MODEL_S40,
    MODEL_S40_PRO,
    MODEL_S40C,
    MODEL_X20_MAX,
)
from custom_components.dreame_vacuum.xiaomi.ov21gl import (
    ROBOT_VACUUM_5_PRO as VACUUM_5_PRO_RECORD,
)
from custom_components.dreame_vacuum.xiaomi.ov31gl import (
    ROBOT_VACUUM_5 as VACUUM_5_RECORD,
)
from custom_components.dreame_vacuum.xiaomi.ov42gl import H50_PRO as H50_PRO_RECORD
from custom_components.dreame_vacuum.xiaomi.profile import (
    AI_CAMERA_CONTROLS,
    CAMERA_ROLLER_CONTROLS,
    CAMERA_ROLLER_OMITTED_CONTROLS,
    DETERGENT_TIME_PROPERTIES,
    ENTER_CHECK_MODE,
    EXTENDED_STATION_CONTROLS,
    EXTENDED_STATION_STATES,
    EXTENDED_STATION_TASKS,
    H50_ROLLER_ACTIONS,
    H50_ROLLER_CONTROLS,
    H50_ROLLER_PROPERTIES,
    H50_ROLLER_STATES,
    HAIR_CUTTING_CONTROLS,
    HOST_TANK_WITH_NOT_INSTALLED,
    LIDAR_HARDWARE_CONTROLS,
    MOP_TEMPERATURE,
    ROLLER_CLEANING_MODE,
    ROLLER_CONTROLS,
    S40_CLASS_CONTROLS,
    S40_CLASS_OMITTED_CONTROLS,
    S60_CLASS_ACTIONS,
    S60_CLASS_CONTROLS,
    S60_CLASS_PROPERTIES,
    S60_CLASS_STATES,
    SELF_CHECK_RESULTS,
    SOLID_DIRT_DETECTION,
    STATION_ACTIONS,
    STATION_PROPERTIES,
    STATION_STATISTICS_PROPERTIES,
    STREAM_CONTROLS,
    SUMMON_STATES,
    SWEEP_DUST_ARREST,
    SWEEP_SUMMON_STATES,
    VIBRATION_MOP,
    WORRY_FREE_THROUGH_BUTLER,
    StoredState,
    SummonWireState,
    compose_addresses,
    compose_codes,
    compose_controls,
    control_with_options,
    select_controls,
)
from custom_components.dreame_vacuum.xiaomi.pv11gl import (
    ROBOT_VACUUM_6_MAX as VACUUM_6_MAX_RECORD,
)
from custom_components.dreame_vacuum.xiaomi.pv21gl import (
    ROBOT_VACUUM_6_PRO as VACUUM_6_PRO_RECORD,
)
from custom_components.dreame_vacuum.xiaomi.pv32gl import (
    ROBOT_VACUUM_6 as VACUUM_6_RECORD,
)
from custom_components.dreame_vacuum.xiaomi.pv81gl import S60 as S60_RECORD
from custom_components.dreame_vacuum.xiaomi.qv41gl import (
    H50_PRO_ROLLER as H50_PRO_ROLLER_RECORD,
)
import pytest
from tests.xiaomi.spec_helpers import spec_index

_TOKEN = "00" * 16


def test_resolve_family_returns_none_for_mijia_dreame_and_unknown_models():
    assert resolve_family("xiaomi.vacuum.c102gl") is None
    assert resolve_family("xiaomi.vacuum.c102cn") is None
    assert resolve_family("xiaomi.vacuum.d103cn") is None
    assert resolve_family("xiaomi.vacuum.d110ch") is None
    assert resolve_family("dreame.vacuum.r2228") is None
    assert resolve_family("") is None


def test_s20_plus_state_and_task_values_convert_to_dreame_codes():
    family = resolve_family(MODEL_S20_PLUS)
    assert family is not None
    assert family.is_simple_cleaning_mode is True
    assert family.should_correct_docked_activity is True
    assert family.convert_incoming("STATE", 4) == DreameVacuumState.SWEEPING
    assert family.convert_incoming("STATE", "1") == DreameVacuumState.IDLE
    assert family.convert_incoming("STATE", 7) == DreameVacuumState.REMOTE_CONTROL
    assert family.convert_incoming("STATE", 99) == 99
    assert (
        family.convert_incoming("TASK_STATUS", 4)
        == DreameVacuumTaskStatus.ZONE_CLEANING
    )
    assert (
        family.convert_incoming("TASK_STATUS", 8)
        == DreameVacuumTaskStatus.SEGMENT_CLEANING
    )
    assert "STATUS" not in family.property_overrides
    assert family.property_overrides["STATE"] == {"siid": 2, "piid": 1}
    assert family.action_overrides["RESUME"] == {"siid": 6, "aiid": 1}
    assert "REQUEST_MAP" not in family.action_overrides
    assert family.property_overrides["CLEANING_MODE"] == {"siid": 2, "piid": 3}
    assert family.convert_incoming("CHARGING_STATUS", 3) == 2
    assert family.convert_incoming("CHARGING_STATUS", 1) == 1


def test_x20_max_state_and_actions_follow_its_spec():
    family = resolve_family(MODEL_X20_MAX)
    assert family is not None
    assert (
        family.convert_incoming("STATE", 16) == DreameVacuumState.SWEEPING_AND_MOPPING
    )
    assert family.convert_incoming("STATE", 7) == DreameVacuumState.RETURNING_TO_WASH
    assert family.convert_incoming("STATE", 15) == DreameVacuumState.ERROR
    assert (
        family.convert_incoming("TASK_STATUS", 3)
        == DreameVacuumTaskStatus.SPOT_CLEANING
    )
    assert family.property_overrides["STATE"] == {"siid": 2, "piid": 2}
    assert family.property_overrides["ERROR"] == {"siid": 2, "piid": 3}
    assert family.action_overrides["RESUME"] == {"siid": 2, "aiid": 8}
    assert family.action_overrides["START_AUTO_EMPTY"] == {"siid": 2, "aiid": 18}
    assert family.action_overrides["RESET_DETERGENT"] == {"siid": 18, "aiid": 1}
    assert "REQUEST_MAP" not in family.action_overrides
    assert "RESET_SILVER_ION" not in family.action_overrides
    assert "STATUS" not in family.property_overrides


def test_cleaning_mode_and_suction_shift_only_on_the_wire_edges():
    family = resolve_family(MODEL_S20_PLUS)
    assert family is not None
    assert family.convert_incoming("CLEANING_MODE", 1) == 0
    assert family.convert_incoming("CLEANING_MODE", 0) == 0
    assert family.convert_incoming("SUCTION_LEVEL", "3") == 2
    assert family.convert_incoming("SUCTION_LEVEL", 2.0) == 1
    assert family.convert_outgoing("CLEANING_MODE", 0) == 1
    assert family.convert_outgoing("SUCTION_LEVEL", 2) == 3
    assert family.convert_outgoing("CLEANING_MODE", False) is False
    assert family.convert_outgoing("VOLUME", 4) == 4
    assert family.convert_outgoing("CLEANING_MODE", "1") == "1"
    assert family.convert_incoming("SCHEDULE", "1-2-3") == "1-2-3"
    assert family.convert_incoming("VOLUME", True) is True
    assert family.convert_incoming("VOLUME", {"raw": 1}) == {"raw": 1}


def test_task_status_comes_from_state_when_sweep_type_would_stay_set():
    family = resolve_family(MODEL_X20_MAX)
    assert family is not None
    sweeping = int(DreameVacuumState.SWEEPING)
    assert family.task_status_code(sweeping, 1) == int(DreameVacuumTaskStatus.COMPLETED)
    assert family.task_status_code(sweeping, 3) == int(
        DreameVacuumTaskStatus.AUTO_CLEANING
    )
    assert family.task_status_code(sweeping, None) == int(
        DreameVacuumTaskStatus.AUTO_CLEANING
    )
    assert family.task_status_code(int(DreameVacuumState.PAUSED), None) == int(
        DreameVacuumTaskStatus.AUTO_CLEANING_PAUSED
    )
    assert family.task_status_code(int(DreameVacuumState.ERROR), 2) == int(
        DreameVacuumTaskStatus.COMPLETED
    )
    assert family.task_status_code(None, None) == int(DreameVacuumTaskStatus.COMPLETED)


def test_robot_vacuum_5_composes_the_station_profile_and_extends_status():
    vacuum_5 = resolve_family(MODEL_ROBOT_VACUUM_5)
    x20 = resolve_family(MODEL_X20_MAX)
    assert vacuum_5 is not None
    assert x20 is not None
    shared = set(x20.property_overrides)
    assert shared <= set(vacuum_5.property_overrides)
    for name in shared:
        assert vacuum_5.property_overrides[name] == x20.property_overrides[name]
    assert vacuum_5.action_overrides == x20.action_overrides
    assert (
        vacuum_5.convert_incoming("STATE", 16) == DreameVacuumState.SWEEPING_AND_MOPPING
    )
    assert vacuum_5.convert_incoming("STATE", 22) == DreameVacuumState.WASHING
    assert (
        vacuum_5.convert_incoming("STATE", 23) == DreameVacuumState.CHARGING_COMPLETED
    )
    assert vacuum_5.convert_incoming("STATE", 24) == DreameVacuumState.RETURNING
    assert vacuum_5.convert_incoming("STATE", 25) == 25
    assert (
        vacuum_5.convert_incoming("TASK_STATUS", 10)
        == DreameVacuumTaskStatus.FAST_MAPPING
    )
    assert (
        vacuum_5.convert_incoming("TASK_STATUS", 11)
        == DreameVacuumTaskStatus.AUTO_CLEANING
    )
    assert vacuum_5.property_overrides["TOTAL_CLEANED_AREA"] == {"siid": 2, "piid": 85}
    assert vacuum_5.property_overrides["DETERGENT_TIME_LEFT"] == {"siid": 18, "piid": 4}
    assert "TOTAL_CLEANED_AREA" not in x20.property_overrides
    assert "REQUEST_MAP" not in vacuum_5.action_overrides
    assert "STATUS" not in vacuum_5.property_overrides
    assert x20.controls == ()
    assert resolve_family(MODEL_S20_PLUS).controls == ()
    assert vacuum_5.controls is EXTENDED_STATION_CONTROLS
    assert x20.property_overrides is not STATION_PROPERTIES
    assert x20.property_overrides["STATE"] is not STATION_PROPERTIES["STATE"]
    assert vacuum_5.property_overrides["STATE"] is not x20.property_overrides["STATE"]
    assert vacuum_5.state_by_wire == EXTENDED_STATION_STATES
    assert vacuum_5.state_by_wire is not EXTENDED_STATION_STATES
    assert vacuum_5.task_by_wire == EXTENDED_STATION_TASKS
    assert vacuum_5.task_by_wire is not EXTENDED_STATION_TASKS


def test_s40_pro_reuses_the_station_profile_and_omits_missing_services():
    s40 = resolve_family(MODEL_S40_PRO)
    vacuum_5 = resolve_family(MODEL_ROBOT_VACUUM_5)
    x20 = resolve_family(MODEL_X20_MAX)
    assert s40 is not None
    assert vacuum_5 is not None
    assert x20 is not None
    assert set(s40.property_overrides) == (
        set(x20.property_overrides) - {"DETERGENT_LEFT"}
    ) | set(STATION_STATISTICS_PROPERTIES)
    for name in set(s40.property_overrides) & set(x20.property_overrides):
        assert s40.property_overrides[name] == x20.property_overrides[name]
        assert s40.property_overrides[name] is not x20.property_overrides[name]
    assert set(s40.action_overrides) == set(x20.action_overrides) - {"RESET_DETERGENT"}
    for name in s40.action_overrides:
        assert s40.action_overrides[name] == x20.action_overrides[name]
    assert s40.state_by_wire == vacuum_5.state_by_wire
    assert s40.state_by_wire is not vacuum_5.state_by_wire
    assert s40.task_by_wire == vacuum_5.task_by_wire
    assert s40.convert_incoming("STATE", 8) == 19
    assert s40.convert_incoming("STATE", 22) == DreameVacuumState.WASHING
    shared = {control.key: control for control in EXTENDED_STATION_CONTROLS}
    for control in s40.controls:
        if control.key in shared:
            assert control is shared[control.key]
    omitted = set(shared) - {control.key for control in s40.controls}
    added = {control.key for control in s40.controls} - set(shared)
    assert omitted == {
        "xiaomi_detergent_delivery",
        "xiaomi_detergent_level",
        "xiaomi_dust_arrest_power",
        "xiaomi_dust_bag_life",
        "xiaomi_dust_bag_time_left",
        "xiaomi_enable_mop_wash",
        "xiaomi_laser_position",
        "xiaomi_obstacle_crossing",
        "xiaomi_repeat_wash_mop",
        "xiaomi_reset_dust_bag",
        "xiaomi_start_cut_hair",
        "xiaomi_start_dry",
        "xiaomi_wash_water_temperature",
    }
    assert added == {"xiaomi_cut_hair", "xiaomi_cut_hair_frequency"}
    assert "DETERGENT_LEFT" not in s40.property_overrides
    assert "DETERGENT_TIME_LEFT" not in s40.property_overrides
    assert "RESET_DETERGENT" not in s40.action_overrides


def test_s40_reuses_the_vacuum_5_map_and_the_s40_class_controls():
    s40 = resolve_family(MODEL_S40)
    vacuum_5 = resolve_family(MODEL_ROBOT_VACUUM_5)
    assert s40 is not None
    assert vacuum_5 is not None
    assert s40.property_overrides == vacuum_5.property_overrides
    assert s40.property_overrides is not vacuum_5.property_overrides
    assert s40.action_overrides == vacuum_5.action_overrides
    assert s40.action_overrides is not vacuum_5.action_overrides
    assert s40.state_by_wire == vacuum_5.state_by_wire
    assert s40.state_by_wire is not vacuum_5.state_by_wire
    assert s40.task_by_wire == vacuum_5.task_by_wire
    shared = {control.key: control for control in EXTENDED_STATION_CONTROLS}
    hair = {control.key: control for control in HAIR_CUTTING_CONTROLS}
    added = {control.key: control for control in S40_CLASS_CONTROLS}
    for control in s40.controls:
        if control.key in shared:
            assert control is shared[control.key]
        else:
            assert control is added[control.key]
        if control.key in hair:
            assert control is hair[control.key]
    omitted = set(shared) - {control.key for control in s40.controls}
    assert omitted == set(S40_CLASS_OMITTED_CONTROLS)
    assert {control.key for control in s40.controls} >= set(added)


def test_h40_reuses_the_s40_map_and_omits_detergent_reminder() -> None:
    h40 = resolve_family(MODEL_H40)
    s40 = resolve_family(MODEL_S40)
    assert h40 is not None
    assert s40 is not None
    assert h40.property_overrides == s40.property_overrides
    assert h40.property_overrides is not s40.property_overrides
    assert h40.action_overrides == s40.action_overrides
    assert h40.action_overrides is not s40.action_overrides
    assert h40.state_by_wire == s40.state_by_wire
    assert h40.state_by_wire is not s40.state_by_wire
    assert h40.task_by_wire == s40.task_by_wire
    assert h40.task_by_wire is not s40.task_by_wire
    shared = {control.key: control for control in EXTENDED_STATION_CONTROLS}
    added = {control.key: control for control in S40_CLASS_CONTROLS}
    for control in h40.controls:
        if control.key in shared:
            assert control is shared[control.key]
        else:
            assert control is added[control.key]
    omitted = set(shared) - {control.key for control in h40.controls}
    assert omitted == set(S40_CLASS_OMITTED_CONTROLS) | {"xiaomi_detergent_reminder"}
    assert {control.key for control in h40.controls} == {
        control.key for control in s40.controls
    } - {"xiaomi_detergent_reminder"}


def test_s40c_reuses_the_s40_map_and_replaces_worry_free_mode() -> None:
    s40c = resolve_family(MODEL_S40C)
    s40 = resolve_family(MODEL_S40)
    assert s40c is not None
    assert s40 is not None
    assert s40c.property_overrides == s40.property_overrides
    assert s40c.property_overrides is not s40.property_overrides
    assert s40c.action_overrides == s40.action_overrides
    assert s40c.action_overrides is not s40.action_overrides
    assert s40c.state_by_wire == s40.state_by_wire
    assert s40c.state_by_wire is not s40.state_by_wire
    assert s40c.task_by_wire == s40.task_by_wire
    assert s40c.task_by_wire is not s40.task_by_wire
    shared = {control.key: control for control in EXTENDED_STATION_CONTROLS}
    added = {control.key: control for control in S40_CLASS_CONTROLS}
    dropped = {
        "xiaomi_enable_mop_wash",
        "xiaomi_start_cut_hair",
        "xiaomi_stop_cut_hair",
        "xiaomi_stop_dry",
    }
    for control in s40c.controls:
        if control.key == "xiaomi_worry_free_mode":
            assert control is not shared[control.key]
            assert (control.siid, control.piid) == (
                shared[control.key].siid,
                shared[control.key].piid,
            )
            assert [slug for _value, slug in control.options] == [
                "deep_clean",
                "deep_clean_2",
                "general",
                "butler",
                "pet",
            ]
        elif control.key in shared:
            assert control is shared[control.key]
        else:
            assert control is added[control.key]
    omitted = set(shared) - {control.key for control in s40c.controls}
    assert omitted == set(S40_CLASS_OMITTED_CONTROLS) | dropped
    assert {control.key for control in s40c.controls} == {
        control.key for control in s40.controls
    } - dropped
    with pytest.raises(KeyError):
        control_with_options(EXTENDED_STATION_CONTROLS, "missing", ())
    with pytest.raises(KeyError):
        compose_controls(
            EXTENDED_STATION_CONTROLS,
            omitted=frozenset({"xiaomi_alarm"}),
            replaced={"xiaomi_alarm": shared["xiaomi_alarm"]},
        )


def test_robot_vacuum_5_pro_reuses_the_station_profile_and_adds_stream() -> None:
    """Property and action maps stay shared. Stream and worry-free are the diff."""
    pro = resolve_family(MODEL_ROBOT_VACUUM_5_PRO)
    h50 = resolve_family(MODEL_H50_PRO)
    assert pro is not None
    assert h50 is not None
    assert pro.property_overrides == h50.property_overrides
    assert pro.property_overrides is not h50.property_overrides
    assert pro.action_overrides == h50.action_overrides
    assert pro.action_overrides is not h50.action_overrides
    assert pro.state_by_wire == h50.state_by_wire
    assert pro.state_by_wire is not h50.state_by_wire
    assert pro.task_by_wire == h50.task_by_wire
    assert pro.task_by_wire is not h50.task_by_wire
    shared = {control.key: control for control in EXTENDED_STATION_CONTROLS}
    added = {control.key: control for control in S40_CLASS_CONTROLS}
    stream = {control.key: control for control in STREAM_CONTROLS}
    for control in pro.controls:
        if control.key == "xiaomi_worry_free_mode":
            assert control is not shared[control.key]
            assert [slug for _value, slug in control.options] == [
                "silent",
                "deep_clean",
                "standard",
                "butler",
                "pet",
            ]
        elif control.key == "xiaomi_solid_dirt_detection":
            assert control is SOLID_DIRT_DETECTION
        elif control.key in stream:
            assert control is stream[control.key]
        elif control.key in shared:
            assert control is shared[control.key]
        else:
            assert control is added[control.key]
    present = {control.key for control in pro.controls}
    assert set(stream) <= present
    assert "xiaomi_self_check_results" not in present
    assert "xiaomi_laser_position" in present
    assert "xiaomi_obstacle_crossing" in present
    assert {control.key for control in h50.controls} - present == {
        "xiaomi_self_check_results"
    }


def test_h50_pro_reuses_the_s40_map_and_restores_published_controls() -> None:
    h50 = resolve_family(MODEL_H50_PRO)
    s40 = resolve_family(MODEL_S40)
    assert h50 is not None
    assert s40 is not None
    assert h50.property_overrides == s40.property_overrides
    assert h50.property_overrides is not s40.property_overrides
    assert h50.action_overrides == s40.action_overrides
    assert h50.action_overrides is not s40.action_overrides
    assert h50.state_by_wire == s40.state_by_wire
    assert h50.state_by_wire is not s40.state_by_wire
    assert h50.task_by_wire == s40.task_by_wire
    assert h50.task_by_wire is not s40.task_by_wire
    shared = {control.key: control for control in EXTENDED_STATION_CONTROLS}
    added = {control.key: control for control in S40_CLASS_CONTROLS}
    extra = {"xiaomi_self_check_results", "xiaomi_solid_dirt_detection"}
    for control in h50.controls:
        if control.key in shared:
            assert control is shared[control.key]
        elif control.key in added:
            assert control is added[control.key]
        elif control.key == "xiaomi_solid_dirt_detection":
            assert control is SOLID_DIRT_DETECTION
        else:
            assert control is SELF_CHECK_RESULTS
    omitted = set(shared) - {control.key for control in h50.controls}
    assert omitted == set(LIDAR_HARDWARE_CONTROLS)
    restored = set(S40_CLASS_OMITTED_CONTROLS) - omitted
    assert {control.key for control in h50.controls} == (
        {control.key for control in s40.controls} | restored | extra
    )


def test_h50_reuses_the_station_profile_and_adds_stream_and_self_check() -> None:
    """Property and action maps stay shared. Drying time is the value-list diff."""
    h50 = resolve_family(MODEL_H50)
    pro = resolve_family(MODEL_ROBOT_VACUUM_5_PRO)
    h50_pro = resolve_family(MODEL_H50_PRO)
    assert h50 is not None
    assert pro is not None
    assert h50_pro is not None
    assert h50.property_overrides == pro.property_overrides
    assert h50.property_overrides is not pro.property_overrides
    assert h50.action_overrides == pro.action_overrides
    assert h50.action_overrides is not pro.action_overrides
    assert h50.state_by_wire == pro.state_by_wire
    assert h50.state_by_wire is not pro.state_by_wire
    assert h50.task_by_wire == pro.task_by_wire
    assert h50.task_by_wire is not pro.task_by_wire
    shared = {control.key: control for control in EXTENDED_STATION_CONTROLS}
    added = {control.key: control for control in S40_CLASS_CONTROLS}
    stream = {control.key: control for control in STREAM_CONTROLS}
    for control in h50.controls:
        if control.key == "xiaomi_drying_time":
            assert control is not shared[control.key]
            assert [slug for _value, slug in control.options] == [
                "hours_2",
                "hours_3",
                "hours_4",
                "hours_5",
                "hours_6",
                "hours_7",
                "hours_8",
                "hours_9",
                "hours_10",
                "hours_11",
                "hours_12",
            ]
        elif control.key == "xiaomi_solid_dirt_detection":
            assert control is SOLID_DIRT_DETECTION
        elif control.key == "xiaomi_self_check_results":
            assert control is SELF_CHECK_RESULTS
        elif control.key in stream:
            assert control is stream[control.key]
        elif control.key in shared:
            assert control is shared[control.key]
        else:
            assert control is added[control.key]
    present = {control.key for control in h50.controls}
    assert set(stream) <= present
    assert LIDAR_HARDWARE_CONTROLS.isdisjoint(present)
    pro_keys = {control.key for control in pro.controls}
    h50_pro_keys = {control.key for control in h50_pro.controls}
    assert pro_keys - present == set(LIDAR_HARDWARE_CONTROLS)
    assert present - pro_keys == {"xiaomi_self_check_results"}
    assert present - h50_pro_keys == set(stream)


def test_h50_pro_publishes_the_s40_omissions_it_maps() -> None:
    """Controls the S40 spec skips are mapped when this spec publishes them."""
    specs = spec_index("ov42gl.json")
    by_key = {control.key: control for control in EXTENDED_STATION_CONTROLS}
    still_absent = frozenset({"xiaomi_laser_position", "xiaomi_obstacle_crossing"})
    h50 = resolve_family(MODEL_H50_PRO)
    assert h50 is not None
    present = {control.key for control in h50.controls}
    assert still_absent.isdisjoint(present)
    for key in S40_CLASS_OMITTED_CONTROLS:
        control = by_key[key]
        address = ("property", control.siid, control.piid)
        if key in still_absent:
            assert address not in specs
            continue
        assert address in specs
        assert key in present


def test_robot_vacuum_6_keeps_shared_controls_and_adds_the_roller() -> None:
    """The roller, camera pair, and value-list edits are the only local diff."""
    vacuum = resolve_family(MODEL_ROBOT_VACUUM_6)
    h50 = resolve_family(MODEL_H50)
    assert vacuum is not None
    assert h50 is not None
    assert set(vacuum.property_overrides) == set(h50.property_overrides) - {
        "CLEANING_MODE",
        "MOP_PAD_LEFT",
        "MOP_PAD_TIME_LEFT",
        "DETERGENT_LEFT",
        "DETERGENT_TIME_LEFT",
    }
    assert set(vacuum.action_overrides) == set(h50.action_overrides) - {
        "RESET_MOP_PAD",
        "RESET_DETERGENT",
    }
    assert set(vacuum.state_by_wire) == set(h50.state_by_wire) - {22, 23}
    assert vacuum.task_by_wire == h50.task_by_wire
    assert vacuum.task_by_wire is not h50.task_by_wire
    shared = {control.key: control for control in EXTENDED_STATION_CONTROLS}
    added = {
        control.key: control
        for control in (
            ROLLER_CLEANING_MODE,
            *AI_CAMERA_CONTROLS,
            SELF_CHECK_RESULTS,
            SWEEP_DUST_ARREST,
            *ROLLER_CONTROLS,
        )
    }
    for control in vacuum.controls:
        if control.key in {"xiaomi_worry_free_mode", "xiaomi_host_tank"}:
            assert control is not shared[control.key]
        elif control.key in shared:
            assert control is shared[control.key]
        else:
            assert control is added[control.key]
    present = {control.key for control in vacuum.controls}
    assert set(added) <= present
    assert "xiaomi_start_mop" not in present
    assert "xiaomi_solid_dirt_detection" not in present
    assert "xiaomi_find_pet" not in present
    worry_free = next(
        control
        for control in vacuum.controls
        if control.key == "xiaomi_worry_free_mode"
    )
    host_tank = next(
        control for control in vacuum.controls if control.key == "xiaomi_host_tank"
    )
    assert [slug for _value, slug in worry_free.options] == [
        "silent_clean",
        "deep_clean",
        "general",
        "butler",
    ]
    assert [value for value, _slug in host_tank.options] == [0, 1, 2, 3, 4]
    cleaning_mode = next(
        control for control in vacuum.controls if control.key == "xiaomi_cleaning_mode"
    )
    assert [value for value, _slug in cleaning_mode.options] == [1, 3, 4]
    assert "CLEANING_MODE" not in vacuum.property_overrides


def test_robot_vacuum_6_max_reuses_the_station_profile() -> None:
    """Only the spec's own omissions and additions differ from the shared lists."""
    vacuum = resolve_family(MODEL_ROBOT_VACUUM_6_MAX)
    vacuum_6 = resolve_family(MODEL_ROBOT_VACUUM_6)
    assert vacuum is not None
    assert vacuum_6 is not None
    assert set(vacuum.property_overrides) == set(vacuum_6.property_overrides) | {
        "MOP_PAD_LEFT",
        "MOP_PAD_TIME_LEFT",
        "DETERGENT_LEFT",
        "DETERGENT_TIME_LEFT",
    }
    assert set(vacuum.action_overrides) == set(vacuum_6.action_overrides) | {
        "RESET_MOP_PAD",
        "RESET_DETERGENT",
    }
    assert set(vacuum.state_by_wire) == set(vacuum_6.state_by_wire) | {25, 26, 27}
    assert vacuum.task_by_wire == vacuum_6.task_by_wire
    assert vacuum.task_by_wire is not vacuum_6.task_by_wire
    shared = {control.key: control for control in EXTENDED_STATION_CONTROLS}
    added_keys = {
        "xiaomi_auto_night_fill_light",
        "xiaomi_ai_wake_up",
        "xiaomi_cleaning_mode",
        "xiaomi_dirt_detection",
        "xiaomi_edge_sweep_frequency",
        "xiaomi_enter_check_mode",
        "xiaomi_flash_light",
        "xiaomi_mop_auto_lift",
        "xiaomi_mop_temperature",
        "xiaomi_object_detection",
        "xiaomi_real_scene_capture",
        "xiaomi_room_detection",
        "xiaomi_self_check_results",
        "xiaomi_stream_enabled",
        "xiaomi_stream_physical_lock",
        "xiaomi_stream_visible_to_shared_users",
        "xiaomi_sweep_ai_detection",
        "xiaomi_sweep_dust_arrest",
        "xiaomi_video_recording_warnings",
        "xiaomi_auto_wash_roller",
        "xiaomi_reset_roller",
        "xiaomi_roller_life",
        "xiaomi_roller_outswing",
        "xiaomi_roller_time_left",
        "xiaomi_start_roller_wash",
        "xiaomi_stop_roller_wash",
    }
    present = {control.key: control for control in vacuum.controls}
    omitted = {
        "xiaomi_calibrate_imu",
        "xiaomi_dust_arrest_power",
        "xiaomi_start_cut_hair",
        "xiaomi_start_mop",
        "xiaomi_start_station_self_clean",
        "xiaomi_stop_cut_hair",
        "xiaomi_stop_station_self_clean",
    }
    for key, control in present.items():
        if key in {"xiaomi_worry_free_mode", "xiaomi_host_tank"}:
            assert control is not shared[key]
        elif key in shared:
            assert control is shared[key]
    assert set(present) - set(shared) == added_keys
    assert set(shared) - set(present) == omitted
    assert present["xiaomi_worry_free_mode"] is WORRY_FREE_THROUGH_BUTLER
    assert present["xiaomi_host_tank"] is HOST_TANK_WITH_NOT_INSTALLED
    assert vacuum_6.controls
    assert WORRY_FREE_THROUGH_BUTLER in vacuum_6.controls
    assert HOST_TANK_WITH_NOT_INSTALLED in vacuum_6.controls
    assert present["xiaomi_mop_temperature"] is MOP_TEMPERATURE
    assert present["xiaomi_enter_check_mode"] is ENTER_CHECK_MODE
    assert vacuum.state_by_wire[25] == -1
    assert vacuum.state_by_wire[26] == int(StoredState.CLEAN_SUMMON)
    assert vacuum.state_by_wire[27] == int(StoredState.SWEEPING)
    assert "CLEANING_MODE" not in vacuum.property_overrides
    with pytest.raises(KeyError):
        select_controls(EXTENDED_STATION_CONTROLS, ("missing",))


def test_robot_vacuum_6_pro_reuses_the_camera_roller_profile() -> None:
    """Only mop life, station assist, and pet mode differ from Robot Vacuum 6 Max."""
    vacuum = resolve_family(MODEL_ROBOT_VACUUM_6_PRO)
    vacuum_6_max = resolve_family(MODEL_ROBOT_VACUUM_6_MAX)
    assert vacuum is not None
    assert vacuum_6_max is not None
    assert set(vacuum.property_overrides) == set(vacuum_6_max.property_overrides) - {
        "MOP_PAD_LEFT",
        "MOP_PAD_TIME_LEFT",
    }
    assert set(vacuum.action_overrides) == set(vacuum_6_max.action_overrides) - {
        "RESET_MOP_PAD"
    }
    assert vacuum.property_overrides is not vacuum_6_max.property_overrides
    assert vacuum.task_by_wire == vacuum_6_max.task_by_wire
    assert vacuum.task_by_wire is not vacuum_6_max.task_by_wire
    assert set(vacuum.state_by_wire) == (set(vacuum_6_max.state_by_wire) - {27}) | {
        22,
        23,
    }
    assert vacuum.state_by_wire[22] == int(StoredState.WASHING)
    assert vacuum.state_by_wire[23] == int(StoredState.CHARGING_COMPLETED)
    assert vacuum.state_by_wire[int(SummonWireState.SELF_CHECK)] == int(
        DreameVacuumState.UNKNOWN
    )
    assert vacuum.state_by_wire[int(SummonWireState.SUMMONING)] == int(
        StoredState.CLEAN_SUMMON
    )
    assert int(SummonWireState.SWEEP_SUMMONING) not in vacuum.state_by_wire
    assert (
        vacuum.state_by_wire[int(SummonWireState.SELF_CHECK)]
        == SUMMON_STATES[int(SummonWireState.SELF_CHECK)]
    )
    shared_worry = next(
        control
        for control in EXTENDED_STATION_CONTROLS
        if control.key == "xiaomi_worry_free_mode"
    )
    max_controls = {control.key: control for control in vacuum_6_max.controls}
    present = {control.key: control for control in vacuum.controls}
    assert set(present) == set(max_controls)
    for key, control in present.items():
        if key == "xiaomi_worry_free_mode":
            assert control is shared_worry
            assert control is not max_controls[key]
        else:
            assert control is max_controls[key]
    assert present["xiaomi_host_tank"] is HOST_TANK_WITH_NOT_INSTALLED
    assert [slug for _value, slug in present["xiaomi_worry_free_mode"].options] == [
        "silent_clean",
        "deep_clean",
        "general",
        "butler",
        "pet",
    ]
    assert set(CAMERA_ROLLER_CONTROLS) <= set(vacuum.controls)
    assert CAMERA_ROLLER_OMITTED_CONTROLS.isdisjoint(present)
    assert "CLEANING_MODE" not in vacuum.property_overrides
    assert "MOP_PAD_LEFT" not in vacuum.property_overrides
    assert "RESET_MOP_PAD" not in vacuum.action_overrides


def test_x20_pro_reuses_the_x20_max_map_and_omits_unpublished_controls() -> None:
    """Dreame addresses match X20 Max. Remote uses the old code, not 23."""
    vacuum = resolve_family(MODEL_X20_PRO)
    x20 = resolve_family(MODEL_X20_MAX)
    assert vacuum is not None
    assert x20 is not None
    assert vacuum.property_overrides == x20.property_overrides
    assert vacuum.property_overrides is not x20.property_overrides
    assert vacuum.action_overrides == x20.action_overrides
    assert vacuum.action_overrides is not x20.action_overrides
    assert vacuum.task_by_wire == x20.task_by_wire
    assert vacuum.task_by_wire is not x20.task_by_wire
    assert set(vacuum.state_by_wire) == set(x20.state_by_wire)
    assert vacuum.state_by_wire[8] == 19
    assert x20.state_by_wire[8] == int(DreameVacuumState.REMOTE_CONTROL)
    assert 22 not in vacuum.state_by_wire
    assert 23 not in vacuum.state_by_wire
    assert 24 not in vacuum.state_by_wire
    shared = {control.key: control for control in EXTENDED_STATION_CONTROLS}
    present = {control.key: control for control in vacuum.controls}
    swing = next(
        control
        for control in S40_CLASS_CONTROLS
        if control.key == "xiaomi_edge_sweep_frequency"
    )
    tail = next(
        control
        for control in S40_CLASS_CONTROLS
        if control.key == "xiaomi_edge_swing_tail_sweep"
    )
    assert present["xiaomi_edge_sweep_frequency"] is not swing
    assert present["xiaomi_mop_wash_area"] is not shared["xiaomi_mop_wash_area"]
    assert present["xiaomi_edge_swing_tail_sweep"] is tail
    for key, control in present.items():
        if key in {"xiaomi_mop_wash_area", "xiaomi_edge_sweep_frequency"}:
            continue
        if key in shared:
            assert control is shared[key]
    assert set(present) - set(shared) == {
        "xiaomi_edge_sweep_frequency",
        "xiaomi_edge_swing_tail_sweep",
    }
    assert "xiaomi_worry_free_mode" not in present
    assert "xiaomi_mop_outer_swing" not in present
    assert "TOTAL_CLEANED_AREA" not in vacuum.property_overrides
    assert "DETERGENT_TIME_LEFT" not in vacuum.property_overrides
    assert "REQUEST_MAP" not in vacuum.action_overrides


def test_s60_models_reuse_the_s60_class_profile() -> None:
    """S60+ adds the auto-empty dock. S60 adds stop-cut-hair and nothing else."""
    s60_plus = resolve_family(MODEL_S60_PLUS)
    s60 = resolve_family(MODEL_S60)
    assert s60_plus is not None
    assert s60 is not None
    assert s60_plus.property_overrides.keys() == S60_CLASS_PROPERTIES.keys()
    assert s60_plus.property_overrides is not S60_CLASS_PROPERTIES
    assert set(s60.property_overrides) == set(S60_CLASS_PROPERTIES) - {
        "AUTO_DUST_COLLECTING",
        "AUTO_EMPTY_FREQUENCY",
    }
    assert s60.property_overrides is not s60_plus.property_overrides
    assert set(s60_plus.action_overrides) == set(S60_CLASS_ACTIONS)
    assert set(s60.action_overrides) == set(S60_CLASS_ACTIONS) - {"START_AUTO_EMPTY"}
    assert s60_plus.task_by_wire == s60.task_by_wire == EXTENDED_STATION_TASKS
    assert s60_plus.task_by_wire is not s60.task_by_wire
    assert s60_plus.state_by_wire == s60.state_by_wire == S60_CLASS_STATES
    assert s60_plus.state_by_wire is not S60_CLASS_STATES
    assert s60_plus.state_by_wire[8] == 19
    assert s60_plus.state_by_wire[22] == int(StoredState.WASHING)
    assert s60_plus.state_by_wire[26] == int(StoredState.CLEAN_SUMMON)
    assert (
        s60_plus.state_by_wire[int(SummonWireState.SWEEP_SUMMONING)]
        == SWEEP_SUMMON_STATES[int(SummonWireState.SWEEP_SUMMONING)]
    )
    shared = {control.key: control for control in S60_CLASS_CONTROLS}
    plus = {control.key: control for control in s60_plus.controls}
    plain = {control.key: control for control in s60.controls}
    assert set(shared) <= set(plus)
    assert set(shared) <= set(plain)
    for key, control in shared.items():
        assert plus[key] is control
        assert plain[key] is control
    assert plus["xiaomi_vibration_mop"] is VIBRATION_MOP
    assert plain["xiaomi_vibration_mop"] is VIBRATION_MOP
    dust = {
        "xiaomi_dust_arrest_power",
        "xiaomi_dust_bag_life",
        "xiaomi_dust_bag_time_left",
        "xiaomi_reset_dust_bag",
        "xiaomi_sweep_dust_arrest",
    }
    assert set(plus) - set(shared) == dust
    assert set(plain) - set(shared) == {"xiaomi_stop_cut_hair"}
    assert plus["xiaomi_sweep_dust_arrest"] is SWEEP_DUST_ARREST
    assert "xiaomi_stop_cut_hair" not in plus
    assert "DETERGENT_LEFT" not in s60_plus.property_overrides
    assert "RESET_DETERGENT" not in s60_plus.action_overrides
    assert "CLEANING_MODE" in s60.property_overrides
    extended = {control.key: control for control in EXTENDED_STATION_CONTROLS}
    assert plus["xiaomi_worry_free_mode"] is extended["xiaomi_worry_free_mode"]
    assert [slug for _value, slug in plus["xiaomi_worry_free_mode"].options][-1] == (
        "pet"
    )


def test_h50_roller_models_share_the_roller_profile_and_declare_differences():
    """H50 Pro Roller adds eject and AI detection. H50 Roller publishes mop-only."""
    pro = resolve_family(MODEL_H50_PRO_ROLLER)
    plain = resolve_family(MODEL_H50_ROLLER)
    assert pro is not None
    assert plain is not None
    assert set(pro.property_overrides) == set(H50_ROLLER_PROPERTIES) - {"CLEANING_MODE"}
    assert pro.property_overrides is not H50_ROLLER_PROPERTIES
    assert plain.property_overrides == H50_ROLLER_PROPERTIES
    assert plain.property_overrides is not H50_ROLLER_PROPERTIES
    assert plain.property_overrides["CLEANING_MODE"]["piid"] == 4
    assert pro.action_overrides == plain.action_overrides == H50_ROLLER_ACTIONS
    assert pro.action_overrides is not H50_ROLLER_ACTIONS
    assert pro.task_by_wire == plain.task_by_wire == EXTENDED_STATION_TASKS
    assert pro.state_by_wire == H50_ROLLER_STATES
    assert pro.state_by_wire is not H50_ROLLER_STATES
    assert 22 not in pro.state_by_wire
    assert 23 not in pro.state_by_wire
    assert plain.state_by_wire == S60_CLASS_STATES
    assert plain.state_by_wire is not S60_CLASS_STATES
    assert plain.state_by_wire[8] == 19
    assert plain.state_by_wire[22] == int(StoredState.WASHING)
    assert plain.state_by_wire[26] == int(StoredState.CLEAN_SUMMON)
    shared = {control.key: control for control in H50_ROLLER_CONTROLS}
    pro_controls = {control.key: control for control in pro.controls}
    plain_controls = {control.key: control for control in plain.controls}
    assert set(shared) <= set(pro_controls)
    for key, control in shared.items():
        assert pro_controls[key] is control
    assert set(pro_controls) - set(shared) == {
        "xiaomi_start_eject",
        "xiaomi_sweep_ai_detection",
    }
    assert pro_controls["xiaomi_worry_free_mode"] is WORRY_FREE_THROUGH_BUTLER
    assert pro_controls["xiaomi_host_tank"] is HOST_TANK_WITH_NOT_INSTALLED
    assert [value for value, _slug in pro_controls["xiaomi_cleaning_mode"].options] == [
        1,
        3,
        4,
    ]
    assert "CLEANING_MODE" not in pro.property_overrides
    assert "xiaomi_cleaning_mode" not in plain_controls
    assert "CLEANING_MODE" in plain.property_overrides
    extended = {control.key: control for control in EXTENDED_STATION_CONTROLS}
    assert (
        plain_controls["xiaomi_worry_free_mode"] is extended["xiaomi_worry_free_mode"]
    )
    assert [slug for _value, slug in plain_controls["xiaomi_worry_free_mode"].options][
        -1
    ] == "pet"
    assert set(plain_controls) - set(shared) == {
        "xiaomi_calibrate_imu",
        "xiaomi_dust_arrest_power",
        "xiaomi_mop_auto_lift",
        "xiaomi_sewage_tank",
        "xiaomi_start_mop",
        "xiaomi_start_mop_wash",
        "xiaomi_station_water_level",
    }
    for key in (
        "xiaomi_auto_water_change",
        "xiaomi_brush_outswing",
        "xiaomi_hot_water_wash",
        "xiaomi_mop_outer_swing",
        "xiaomi_start_eject",
        "xiaomi_sweep_ai_detection",
    ):
        assert key not in plain_controls
    assert "MOP_PAD_LEFT" not in pro.property_overrides
    assert "RESET_DETERGENT" not in pro.action_overrides
    assert "DETERGENT_LEFT" not in plain.property_overrides


def test_compose_rejects_an_omission_the_profile_does_not_define():
    with pytest.raises(KeyError):
        compose_addresses(STATION_PROPERTIES, omitted=frozenset({"NO_SUCH"}))
    with pytest.raises(KeyError):
        compose_controls(EXTENDED_STATION_CONTROLS, omitted=frozenset({"missing"}))
    with pytest.raises(KeyError):
        compose_codes(EXTENDED_STATION_STATES, omitted=(999,))


def test_station_address_literals_are_declared_once():
    """Station address dicts are written only in the shared profile."""
    root = Path("custom_components/dreame_vacuum/xiaomi")
    profile = (root / "profile.py").read_text(encoding="utf-8")
    for name in (
        "d102gl.py",
        "d109gl.py",
        "e101gb.py",
        "ov21gl.py",
        "ov31gl.py",
        "ov42gl.py",
        "ov43gb.py",
        "pv11gl.py",
        "pv21gl.py",
        "pv32gl.py",
        "pv51gl.py",
        "pv81gl.py",
        "qv41gl.py",
        "qv42gl.py",
        "ov51gl.py",
        "ov71gl.py",
        "ov81gl.py",
        "ov21cn.py",
        "ov31cn.py",
        "ov42cn.py",
        "pv32cn.py",
        "qv41cn.py",
        "c101.py",
        "c103.py",
        "d102ev.py",
        "pv11cn.py",
        "pv21cn.py",
        "qv12cn.py",
        "c107.py",
        "d101.py",
        "ov81cn.py",
        "pv31cn.py",
    ):
        text = (root / name).read_text(encoding="utf-8")
        assert "siid" not in text, name
        assert "aiid" not in text, name
    for mapping in STATION_PROPERTIES.values():
        needle = f'{{"siid": {mapping["siid"]}, "piid": {mapping["piid"]}}}'
        assert profile.count(needle) == 1
    for mapping in STATION_ACTIONS.values():
        needle = f'{{"siid": {mapping["siid"]}, "aiid": {mapping["aiid"]}}}'
        assert profile.count(needle) == 1
    for mapping in {
        **STATION_STATISTICS_PROPERTIES,
        **DETERGENT_TIME_PROPERTIES,
    }.values():
        needle = f'{{"siid": {mapping["siid"]}, "piid": {mapping["piid"]}}}'
        assert profile.count(needle) == 1


def test_controls_of_ignores_devices_without_a_xiaomi_codec():
    assert controls_of(object()) == ()
    assert controls_of(SimpleNamespace(_property_codec=object())) == ()
    family = resolve_family(MODEL_ROBOT_VACUUM_5)
    assert family is not None
    device = SimpleNamespace(_property_codec=family)
    assert controls_of(device) == family.controls
    assert "xiaomi_alarm" in control_keys(device, "switch")
    assert control_keys(device, "vacuum") == frozenset()
    assert control_keys(SimpleNamespace(), "switch") == frozenset()


def test_property_and_action_names_exist_on_the_dreame_enums():
    for model in (
        MODEL_S20_PLUS,
        MODEL_X20_MAX,
        MODEL_ROBOT_VACUUM_5,
        MODEL_S40_PRO,
        MODEL_S40,
        MODEL_H40,
        MODEL_H50,
        MODEL_H50_PRO,
        MODEL_S40C,
        MODEL_ROBOT_VACUUM_5_PRO,
        MODEL_ROBOT_VACUUM_6,
        MODEL_ROBOT_VACUUM_6_MAX,
        MODEL_ROBOT_VACUUM_6_PRO,
        MODEL_S60,
        MODEL_S60_PLUS,
        MODEL_H50_PRO_ROLLER,
        MODEL_H50_ROLLER,
        MODEL_X20_PRO,
        MODEL_MIJIA_ROBOT_VACUUM_6,
        MODEL_MIJIA_7C,
        MODEL_MIJIA_M40_S,
        MODEL_MIJIA_5_PRO,
        MODEL_MIJIA_5C,
        MODEL_MIJIA_SWEEP_MOP_2,
        MODEL_MIJIA_SWEEP_MOP_3,
        MODEL_MIJIA_3C,
        MODEL_MIJIA_M30,
        MODEL_MIJIA_6_MAX,
        MODEL_MIJIA_6_PRO,
        MODEL_MIJIA_7_MAX,
        MODEL_MIJIA_H40,
        MODEL_MIJIA_M30_PRO,
        MODEL_MIJIA_ROBOT_VACUUM_4,
        MODEL_MIJIA_ROBOT_VACUUM_5,
    ):
        family = resolve_family(model)
        assert family is not None
        for name in family.property_overrides:
            DreameVacuumProperty[name]
        for name in family.action_overrides:
            DreameVacuumAction[name]


def test_chinese_variants_leave_the_global_records_unchanged():
    """A regional record copies or aliases its global model and does not replace it."""
    assert resolve_family(MODEL_ROBOT_VACUUM_6) is VACUUM_6_RECORD
    assert resolve_family(MODEL_H50_PRO_ROLLER) is H50_PRO_ROLLER_RECORD
    assert resolve_family(MODEL_ROBOT_VACUUM_5) is VACUUM_5_RECORD
    assert resolve_family(MODEL_ROBOT_VACUUM_5_PRO) is VACUUM_5_PRO_RECORD
    assert resolve_family(MODEL_H50_PRO) is H50_PRO_RECORD
    assert resolve_family(MODEL_MIJIA_5C).controls is H50_PRO_RECORD.controls
    assert resolve_family(MODEL_X20) is X20_RECORD
    assert resolve_family(MODEL_S20) is S20_RECORD
    assert resolve_family(MODEL_X20_PRO) is X20_PRO_RECORD
    assert resolve_family(MODEL_S60) is S60_RECORD
    assert resolve_family(MODEL_MIJIA_M30) is M30_RECORD
    assert resolve_family(MODEL_ROBOT_VACUUM_6_MAX) is VACUUM_6_MAX_RECORD
    assert resolve_family(MODEL_ROBOT_VACUUM_6_PRO) is VACUUM_6_PRO_RECORD
    assert resolve_family(MODEL_MIJIA_SWEEP_MOP_2).controls is X20_RECORD.controls


def test_build_property_transport_skips_cloud_fallback_cases():
    family = resolve_family(MODEL_S20_PLUS)
    assert family is not None
    assert family.build_property_transport("", _TOKEN) is None
    assert family.build_property_transport("127.0.0.1", "zz") is None
    transport = family.build_property_transport("127.0.0.1", _TOKEN)
    assert transport is not None
    assert "127.0.0.1" not in repr(transport)
    assert _TOKEN not in repr(transport)
