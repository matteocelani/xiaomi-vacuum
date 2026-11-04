"""Dreame capability lists stay put. Xiaomi flags come from mapped names."""

from __future__ import annotations

import base64
from dataclasses import replace
import json
from types import SimpleNamespace
import zlib

from custom_components.dreame_vacuum.dreame.const import DEVICE_INFO
from custom_components.dreame_vacuum.dreame.family_codec import apply_family
from custom_components.dreame_vacuum.dreame.types import (
    DreameVacuumDeviceCapability,
    RobotType,
)
from custom_components.dreame_vacuum.xiaomi.mapping import resolve_family

_CATALOG = json.loads(
    zlib.decompress(base64.b64decode(DEVICE_INFO), zlib.MAX_WBITS | 32)
)
_DREAME_P2008 = (
    "lidar_navigation",
    "object_shift",
    "disable_sensor_cleaning",
    "sweep_with_mop",
)
_MIJIA_C102GL = (
    "lidar_navigation",
    "mop_pad_lifting",
    "mopping_after_sweeping",
    "disable_sensor_cleaning",
    "auto_rename_segment",
    "mop_clean_frequency",
    "obstacles",
    "new_state",
    "mijia",
    "auto_emptying",
    "no_detergent",
    "custom_cleaning_mode",
)
_MOVA_R2430 = (
    "lidar_navigation",
    "mop_pad_lifting",
    "mop_pad_lifting_plus",
    "mopping_after_sweeping",
    "fill_light",
    "hot_washing",
    "max_suction_power",
    "obstacle_image_crop",
    "uv_sterilization",
    "self_clean_frequency",
    "auto_empty_mode",
    "floor_material",
    "floor_material_edit",
    "floor_direction_cleaning",
    "segment_visibility",
    "large_particles_boost",
    "fluid_detection",
    "intensive_carpet_cleaning",
    "mopping_settings",
    "cleaning_route",
    "segment_slow_clean_route",
    "pet_furniture",
    "disable_sensor_cleaning",
    "auto_rename_segment",
    "clean_carpets_first",
    "saved_furnitures",
    "extended_furnitures",
    "furnitures_v2",
    "wetness",
    "wetness_level",
    "obstacles",
    "water_check",
    "auto_carpet_cleaning",
    "segment_mopping_settings",
    "max_suction_power_extended",
    "auto_recleaning",
    "auto_rewashing",
    "new_state",
    "camera_streaming",
    "stream_tx",
    "stream_ali",
    "video_dynamic_vendor",
    "video_during_cleaning",
    "pet_snapshot",
    "video_audio",
    "gen5",
    "cleangenius_mode",
    "side_reach",
    "water_temperature",
    "smart_mop_washing",
    "dnd_functions",
    "ramps",
    "virtual_tracks",
    "side_brush_carpet_rotate",
    "area_rotation",
    "dynamic_obstacle_cleaning",
    "auto_add_detergent",
    "carpet_cleanset_v2",
    "carpet_shape",
    "carpet_id",
    "auto_emptying",
    "disable_mop_consumable",
    "onboard_dirty_water_tank",
    "drying_time_v2",
    "cleaning_sequence_v2",
    "custom_drying_time",
    "walls_v3",
    "quick_map_recovery",
    "curtains",
    "dock_status",
    "skip_area",
    "custom_cleaning_mode",
    "walls",
)
_COPIED_XIAOMI_ROW = (
    "lidar_navigation",
    "mop_pad_lifting",
    "mopping_after_sweeping",
    "disable_sensor_cleaning",
    "auto_rename_segment",
    "mop_clean_frequency",
    "obstacles",
    "new_state",
    "mijia",
    "auto_emptying",
    "custom_cleaning_mode",
)
_S20_PLUS = (
    "dnd",
    "disable_sensor_cleaning",
    "mijia",
)
_X20_MAX = (
    "auto_empty_base",
    "dnd",
    "disable_sensor_cleaning",
    "detergent",
    "mijia",
    "auto_emptying",
)
_S40_PRO = (
    "auto_empty_base",
    "dnd",
    "disable_sensor_cleaning",
    "mijia",
    "auto_emptying",
)


def _load(model: str, codec: object | None) -> DreameVacuumDeviceCapability:
    device = SimpleNamespace(
        info=SimpleNamespace(model=model, version=1),
        get_property=lambda _prop: None,
        _property_codec=codec,
        _map_manager=None,
        status=SimpleNamespace(
            current_segments=None,
            current_map=None,
            selected_map=None,
            fill_light=None,
        ),
    )
    capability = DreameVacuumDeviceCapability(device)
    capability.load(_CATALOG)
    return capability


def test_dreame_and_mijia_capability_lists_are_unchanged():
    assert resolve_family("xiaomi.vacuum.c102gl") is None
    assert resolve_family("dreame.vacuum.p2008") is None
    p2008 = _load("dreame.vacuum.p2008", None)
    c102gl = _load("xiaomi.vacuum.c102gl", None)
    mova = _load("mova.vacuum.r2430", None)
    assert tuple(p2008.list) == _DREAME_P2008
    assert tuple(c102gl.list) == _MIJIA_C102GL
    assert tuple(mova.list) == _MOVA_R2430
    assert p2008.robot_type is RobotType.LIDAR
    assert c102gl.self_wash_base is False
    assert c102gl.lidar_navigation is True


def test_catalog_row_stays_until_the_xiaomi_codec_is_installed():
    for model in (
        "xiaomi.vacuum.b108gl",
        "xiaomi.vacuum.d109gl",
        "xiaomi.vacuum.d102gl",
        "xiaomi.vacuum.ov31gl",
        "xiaomi.vacuum.ov71gl",
        "xiaomi.vacuum.ov81gl",
        "xiaomi.vacuum.ov51gl",
        "xiaomi.vacuum.e101gb",
        "xiaomi.vacuum.ov42gl",
        "xiaomi.vacuum.ov21gl",
        "xiaomi.vacuum.ov43gb",
        "xiaomi.vacuum.pv32gl",
        "xiaomi.vacuum.pv11gl",
        "xiaomi.vacuum.pv21gl",
        "xiaomi.vacuum.pv51gl",
        "xiaomi.vacuum.pv81gl",
        "xiaomi.vacuum.qv41gl",
        "xiaomi.vacuum.qv42gl",
        "xiaomi.vacuum.b112",
        "xiaomi.vacuum.b112gl",
        "xiaomi.vacuum.b112bk",
        "xiaomi.vacuum.c108",
        "xiaomi.vacuum.d106gl",
        "xiaomi.vacuum.c101eu",
        "xiaomi.vacuum.b106eu",
        "xiaomi.vacuum.b106bk",
        "xiaomi.vacuum.pv32cn",
        "xiaomi.vacuum.qv41cn",
        "xiaomi.vacuum.ov31cn",
        "xiaomi.vacuum.ov21cn",
        "xiaomi.vacuum.ov42cn",
        "xiaomi.vacuum.c101",
        "xiaomi.vacuum.c103",
        "xiaomi.vacuum.d102ev",
        "xiaomi.vacuum.pv11cn",
        "xiaomi.vacuum.pv21cn",
        "xiaomi.vacuum.qv12cn",
        "xiaomi.vacuum.pv31cn",
        "xiaomi.vacuum.c107",
        "xiaomi.vacuum.ov81cn",
        "xiaomi.vacuum.d101",
        "xiaomi.vacuum.c104",
    ):
        copied = _load(model, None)
        assert tuple(copied.list) == _COPIED_XIAOMI_ROW
        assert copied.self_wash_base is False
        assert copied.mop_pad_lifting is True


def test_chinese_variants_keep_the_global_capability_list():
    """Controls can differ. Derived flags follow the shared property and action names."""
    pairs = (
        ("xiaomi.vacuum.pv32gl", "xiaomi.vacuum.pv32cn"),
        ("xiaomi.vacuum.qv41gl", "xiaomi.vacuum.qv41cn"),
        ("xiaomi.vacuum.ov31gl", "xiaomi.vacuum.ov31cn"),
        ("xiaomi.vacuum.ov21gl", "xiaomi.vacuum.ov21cn"),
        ("xiaomi.vacuum.ov42gl", "xiaomi.vacuum.ov42cn"),
        ("xiaomi.vacuum.c101eu", "xiaomi.vacuum.c101"),
        ("xiaomi.vacuum.d106gl", "xiaomi.vacuum.c103"),
        ("xiaomi.vacuum.d102gl", "xiaomi.vacuum.d102ev"),
        ("xiaomi.vacuum.pv11gl", "xiaomi.vacuum.pv11cn"),
        ("xiaomi.vacuum.pv21gl", "xiaomi.vacuum.pv21cn"),
        ("xiaomi.vacuum.ov42gl", "xiaomi.vacuum.pv31cn"),
        ("xiaomi.vacuum.d102ev", "xiaomi.vacuum.c107"),
        ("xiaomi.vacuum.pv81gl", "xiaomi.vacuum.ov81cn"),
        ("xiaomi.vacuum.b106eu", "xiaomi.vacuum.c104"),
    )
    for global_model, chinese_model in pairs:
        global_capability = _load(global_model, resolve_family(global_model))
        chinese_capability = _load(chinese_model, resolve_family(chinese_model))
        assert tuple(chinese_capability.list) == tuple(global_capability.list)


def test_s20_plus_and_x20_max_use_the_xiaomi_base():
    s20 = _load("xiaomi.vacuum.b108gl", resolve_family("xiaomi.vacuum.b108gl"))
    x20 = _load("xiaomi.vacuum.d109gl", resolve_family("xiaomi.vacuum.d109gl"))
    x20_pro = _load("xiaomi.vacuum.d102gl", resolve_family("xiaomi.vacuum.d102gl"))
    vacuum_5 = _load("xiaomi.vacuum.ov31gl", resolve_family("xiaomi.vacuum.ov31gl"))
    s40_pro = _load("xiaomi.vacuum.ov71gl", resolve_family("xiaomi.vacuum.ov71gl"))
    s40 = _load("xiaomi.vacuum.ov81gl", resolve_family("xiaomi.vacuum.ov81gl"))
    h40 = _load("xiaomi.vacuum.ov51gl", resolve_family("xiaomi.vacuum.ov51gl"))
    s40c = _load("xiaomi.vacuum.e101gb", resolve_family("xiaomi.vacuum.e101gb"))
    h50 = _load("xiaomi.vacuum.ov42gl", resolve_family("xiaomi.vacuum.ov42gl"))
    vacuum_5_pro = _load("xiaomi.vacuum.ov21gl", resolve_family("xiaomi.vacuum.ov21gl"))
    vacuum_h50 = _load("xiaomi.vacuum.ov43gb", resolve_family("xiaomi.vacuum.ov43gb"))
    vacuum_6 = _load("xiaomi.vacuum.pv32gl", resolve_family("xiaomi.vacuum.pv32gl"))
    vacuum_6_max = _load("xiaomi.vacuum.pv11gl", resolve_family("xiaomi.vacuum.pv11gl"))
    vacuum_6_pro = _load("xiaomi.vacuum.pv21gl", resolve_family("xiaomi.vacuum.pv21gl"))
    s60_plus = _load("xiaomi.vacuum.pv51gl", resolve_family("xiaomi.vacuum.pv51gl"))
    s60 = _load("xiaomi.vacuum.pv81gl", resolve_family("xiaomi.vacuum.pv81gl"))
    h50_pro_roller = _load(
        "xiaomi.vacuum.qv41gl", resolve_family("xiaomi.vacuum.qv41gl")
    )
    h50_roller = _load("xiaomi.vacuum.qv42gl", resolve_family("xiaomi.vacuum.qv42gl"))
    e10 = _load("xiaomi.vacuum.b112", resolve_family("xiaomi.vacuum.b112"))
    e12 = _load("xiaomi.vacuum.b112gl", resolve_family("xiaomi.vacuum.b112gl"))
    e10c = _load("xiaomi.vacuum.b112bk", resolve_family("xiaomi.vacuum.b112bk"))
    e5 = _load("xiaomi.vacuum.c108", resolve_family("xiaomi.vacuum.c108"))
    vacuum_s20 = _load("xiaomi.vacuum.d106gl", resolve_family("xiaomi.vacuum.d106gl"))
    vacuum_x20 = _load("xiaomi.vacuum.c101eu", resolve_family("xiaomi.vacuum.c101eu"))
    vacuum_s12 = _load("xiaomi.vacuum.b106eu", resolve_family("xiaomi.vacuum.b106eu"))
    vacuum_t12 = _load("xiaomi.vacuum.b106bk", resolve_family("xiaomi.vacuum.b106bk"))
    assert tuple(s20.list) == _S20_PLUS
    assert tuple(e10.list) == ("disable_sensor_cleaning", "mijia")
    assert tuple(e12.list) == tuple(e10.list)
    assert tuple(e10c.list) == tuple(e10.list)
    assert tuple(e5.list) == tuple(e10.list)
    assert tuple(vacuum_s20.list) == tuple(e10.list)
    assert tuple(vacuum_x20.list) == tuple(e10.list)
    assert tuple(vacuum_s12.list) == tuple(e10.list)
    assert tuple(vacuum_t12.list) == tuple(e10.list)
    assert e5.dnd is False
    assert e5.self_wash_base is False
    assert e5.lidar_navigation is False
    assert e5.auto_empty_base is False
    assert e10.dnd is False
    assert e10.auto_empty_base is False
    assert vacuum_s20.dnd is False
    assert vacuum_s20.auto_empty_base is False
    assert vacuum_s20.self_wash_base is False
    assert vacuum_s20.lidar_navigation is False
    assert vacuum_x20.dnd is False
    assert vacuum_x20.auto_empty_base is False
    assert vacuum_x20.self_wash_base is False
    assert vacuum_x20.station_cleaning is False
    assert vacuum_x20.lidar_navigation is False
    assert vacuum_s12.dnd is False
    assert vacuum_s12.auto_empty_base is False
    assert vacuum_s12.self_wash_base is False
    assert vacuum_s12.lidar_navigation is False
    assert vacuum_t12.dnd is False
    assert vacuum_t12.auto_empty_base is False
    assert vacuum_t12.self_wash_base is False
    assert vacuum_t12.lidar_navigation is False
    vacuum_c104 = _load("xiaomi.vacuum.c104", resolve_family("xiaomi.vacuum.c104"))
    assert tuple(vacuum_c104.list) == tuple(e10.list)
    assert vacuum_c104.dnd is False
    assert vacuum_c104.auto_empty_base is False
    assert vacuum_c104.self_wash_base is False
    assert vacuum_c104.lidar_navigation is False
    assert tuple(x20.list) == _X20_MAX
    assert tuple(x20_pro.list) == _X20_MAX
    assert tuple(vacuum_5.list) == _X20_MAX
    assert tuple(s40_pro.list) == _S40_PRO
    assert tuple(s40.list) == _X20_MAX
    assert tuple(h40.list) == _X20_MAX
    assert tuple(s40c.list) == _X20_MAX
    assert tuple(h50.list) == _X20_MAX
    for capability in (
        s20,
        x20,
        x20_pro,
        vacuum_5,
        s40_pro,
        s40,
        h40,
        s40c,
        h50,
        vacuum_5_pro,
        vacuum_h50,
        vacuum_6,
        vacuum_6_max,
        vacuum_6_pro,
        s60_plus,
        s60,
        h50_pro_roller,
        h50_roller,
    ):
        assert capability.self_wash_base is False
        assert capability.station_cleaning is False
        assert capability.lidar_navigation is False
        assert capability.mop_pad_lifting is False
        assert capability.new_state is False
        assert capability.obstacles is False
        assert capability.carpet_recognition is False
        assert capability.wifi_map is False
        assert capability.backup_map is False
        assert capability.drainage is False
        assert capability.robot_type is RobotType.LIDAR
        assert capability.mijia is True
        assert capability.dnd is True
    assert s20.auto_empty_base is False
    assert s20.auto_emptying is False
    assert s20.detergent is False
    assert x20.auto_empty_base is True
    assert x20.auto_emptying is True
    assert x20.auto_empty_mode is False
    assert x20.detergent is True
    assert x20_pro.auto_empty_base is True
    assert x20_pro.auto_emptying is True
    assert x20_pro.auto_empty_mode is False
    assert x20_pro.detergent is True
    assert x20_pro.self_wash_base is False
    assert x20_pro.station_cleaning is False
    assert vacuum_5.auto_empty_base is True
    assert vacuum_5.auto_emptying is True
    assert vacuum_5.detergent is True
    assert vacuum_5.self_wash_base is False
    assert vacuum_5.lidar_navigation is False
    assert s40_pro.auto_empty_base is True
    assert s40_pro.auto_emptying is True
    assert s40_pro.detergent is False
    assert s40_pro.self_wash_base is False
    assert s40_pro.lidar_navigation is False
    assert s40.auto_empty_base is True
    assert s40.auto_emptying is True
    assert s40.detergent is True
    assert s40.self_wash_base is False
    assert s40.lidar_navigation is False
    assert h40.auto_empty_base is True
    assert h40.auto_emptying is True
    assert h40.detergent is True
    assert h40.self_wash_base is False
    assert h40.lidar_navigation is False
    assert s40c.auto_empty_base is True
    assert s40c.auto_emptying is True
    assert s40c.detergent is True
    assert s40c.self_wash_base is False
    assert s40c.lidar_navigation is False
    assert h50.auto_empty_base is True
    assert h50.auto_emptying is True
    assert h50.detergent is True
    assert h50.self_wash_base is False
    assert h50.lidar_navigation is False
    assert tuple(vacuum_5_pro.list) == _X20_MAX
    assert vacuum_5_pro.auto_empty_base is True
    assert vacuum_5_pro.auto_emptying is True
    assert vacuum_5_pro.detergent is True
    assert vacuum_5_pro.self_wash_base is False
    assert vacuum_5_pro.lidar_navigation is False
    assert tuple(vacuum_h50.list) == _X20_MAX
    assert vacuum_h50.auto_empty_base is True
    assert vacuum_h50.auto_emptying is True
    assert vacuum_h50.detergent is True
    assert vacuum_h50.self_wash_base is False
    assert vacuum_h50.lidar_navigation is False
    assert tuple(vacuum_6.list) == _S40_PRO
    assert vacuum_6.auto_empty_base is True
    assert vacuum_6.auto_emptying is True
    assert vacuum_6.detergent is False
    assert vacuum_6.self_wash_base is False
    assert vacuum_6.lidar_navigation is False
    assert vacuum_6.station_cleaning is False
    assert vacuum_6.dnd is True
    assert tuple(vacuum_6_max.list) == _X20_MAX
    assert vacuum_6_max.auto_empty_base is True
    assert vacuum_6_max.auto_emptying is True
    assert vacuum_6_max.detergent is True
    assert vacuum_6_max.self_wash_base is False
    assert vacuum_6_max.lidar_navigation is False
    assert vacuum_6_max.station_cleaning is False
    assert vacuum_6_max.dnd is True
    assert tuple(vacuum_6_pro.list) == _X20_MAX
    assert vacuum_6_pro.auto_empty_base is True
    assert vacuum_6_pro.auto_emptying is True
    assert vacuum_6_pro.detergent is True
    assert vacuum_6_pro.self_wash_base is False
    assert vacuum_6_pro.lidar_navigation is False
    assert vacuum_6_pro.station_cleaning is False
    assert vacuum_6_pro.dnd is True
    assert tuple(s60_plus.list) == _S40_PRO
    assert s60_plus.auto_empty_base is True
    assert s60_plus.auto_emptying is True
    assert s60_plus.detergent is False
    assert s60_plus.self_wash_base is False
    assert s60_plus.lidar_navigation is False
    assert s60_plus.station_cleaning is False
    assert tuple(s60.list) == _S20_PLUS
    assert s60.auto_empty_base is False
    assert s60.auto_emptying is False
    assert s60.detergent is False
    assert s60.self_wash_base is False
    assert s60.lidar_navigation is False
    assert s60.station_cleaning is False
    assert tuple(h50_pro_roller.list) == _S40_PRO
    assert h50_pro_roller.auto_empty_base is True
    assert h50_pro_roller.auto_emptying is True
    assert h50_pro_roller.detergent is False
    assert h50_pro_roller.self_wash_base is False
    assert h50_pro_roller.lidar_navigation is False
    assert tuple(h50_roller.list) == _S40_PRO
    assert h50_roller.auto_empty_base is True
    assert h50_roller.auto_emptying is True
    assert h50_roller.detergent is False
    assert h50_roller.self_wash_base is False
    assert h50_roller.lidar_navigation is False


def test_a_mapped_wash_base_or_map_turns_only_that_flag_on():
    family = resolve_family("xiaomi.vacuum.b108gl")
    assert family is not None
    wash = replace(
        family,
        property_overrides={
            **family.property_overrides,
            "SELF_WASH_BASE_STATUS": {"siid": 99, "piid": 1},
        },
    )
    washed = _load("xiaomi.vacuum.b108gl", wash)
    assert washed.self_wash_base is True
    assert washed.station_cleaning is False
    assert washed.robot_type is RobotType.MOPPING

    mapped = replace(
        family,
        property_overrides={
            **family.property_overrides,
            "MAP_DATA": {"siid": 99, "piid": 2},
            "SENSOR_DIRTY_LEFT": {"siid": 99, "piid": 3},
        },
    )
    sensor = _load("xiaomi.vacuum.b108gl", mapped)
    assert sensor.lidar_navigation is True
    assert sensor.disable_sensor_cleaning is False
    assert sensor.self_wash_base is False


def test_apply_family_replaces_flags_when_the_capability_is_already_loaded():
    capability = _load("xiaomi.vacuum.b108gl", None)
    assert capability.mop_pad_lifting is True
    family = resolve_family("xiaomi.vacuum.b108gl")
    assert family is not None
    device = SimpleNamespace(
        property_mapping=None,
        action_mapping=None,
        _property_codec=None,
        _map_manager=None,
        _protocol=SimpleNamespace(property_transport=None),
        host="",
        token="",
        capability=capability,
    )
    apply_family(device, family)
    assert capability.mop_pad_lifting is False
    assert capability.self_wash_base is False
    assert tuple(capability.list) == _S20_PLUS


def test_mijia_h40_derives_flags_without_a_dock() -> None:
    """Dust collection and detergent are unpublished, so those flags stay off."""
    capability = _load("xiaomi.vacuum.d101", resolve_family("xiaomi.vacuum.d101"))
    assert tuple(capability.list) == _S20_PLUS
    assert capability.auto_empty_base is False
    assert capability.auto_emptying is False
    assert capability.detergent is False
    assert capability.self_wash_base is False
    assert capability.lidar_navigation is False


def test_mijia_7_max_derives_the_station_flags():
    """Detergent and auto-empty stay on. Wash base and lidar stay off."""
    capability = _load("xiaomi.vacuum.qv12cn", resolve_family("xiaomi.vacuum.qv12cn"))
    assert tuple(capability.list) == _X20_MAX
    assert capability.auto_empty_base is True
    assert capability.auto_emptying is True
    assert capability.detergent is True
    assert capability.dnd is True
    assert capability.self_wash_base is False
    assert capability.station_cleaning is False
    assert capability.lidar_navigation is False
    assert capability.robot_type is RobotType.LIDAR


def test_each_extra_mapped_name_turns_on_its_flag():
    """Names outside the three models still derive the flag the shell expects."""
    family = resolve_family("xiaomi.vacuum.b108gl")
    assert family is not None
    cases = (
        ("DND_TASK", "property", "dnd_task"),
        ("CARPET_RECOGNITION", "property", "carpet_recognition"),
        ("WASHBOARD_CLEANING_STATUS", "property", "station_cleaning"),
        ("DRAINAGE_STATUS", "property", "drainage"),
        ("OFF_PEAK_CHARGING", "property", "off_peak_charging"),
        ("WIFI_MAP", "property", "wifi_map"),
        ("MAP_BACKUP_STATUS", "property", "backup_map"),
        ("MULTI_FLOOR_MAP", "property", "multi_floor_map"),
        ("BACKUP_MAP", "action", "backup_map"),
        ("START_WASHING", "action", "self_wash_base"),
    )
    for name, kind, flag in cases:
        if kind == "property":
            updated = replace(
                family,
                property_overrides={
                    **family.property_overrides,
                    name: {"siid": 99, "piid": 1},
                },
            )
        else:
            updated = replace(
                family,
                action_overrides={
                    **family.action_overrides,
                    name: {"siid": 99, "aiid": 1},
                },
            )
        capability = _load("xiaomi.vacuum.b108gl", updated)
        assert getattr(capability, flag) is True, name
