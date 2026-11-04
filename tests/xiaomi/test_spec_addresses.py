"""Every Xiaomi address must match the bundled MIoT spec, including inherited defaults."""

from __future__ import annotations

import json
from pathlib import Path

from custom_components.dreame_vacuum.dreame.family_codec import apply_family
from custom_components.dreame_vacuum.dreame.types import (
    DreameVacuumAction,
    DreameVacuumActionMapping,
    DreameVacuumProperty,
    DreameVacuumPropertyMapping,
)
from custom_components.dreame_vacuum.xiaomi import (
    MODEL_E5,
    MODEL_E10,
    MODEL_E10C,
    MODEL_E12,
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
    MODEL_MIJIA_ROBOT_VACUUM_4,
    MODEL_MIJIA_ROBOT_VACUUM_5,
    MODEL_MIJIA_ROBOT_VACUUM_6,
    MODEL_MIJIA_SWEEP_MOP_2,
    MODEL_MIJIA_SWEEP_MOP_3,
    MODEL_ROBOT_VACUUM_5_PRO,
    MODEL_ROBOT_VACUUM_6,
    MODEL_ROBOT_VACUUM_6_MAX,
    MODEL_ROBOT_VACUUM_6_PRO,
    MODEL_S12,
    MODEL_S20,
    MODEL_S60,
    MODEL_S60_PLUS,
    MODEL_T12,
    MODEL_X20,
    resolve_family,
)
from custom_components.dreame_vacuum.xiaomi.mapping import (
    MODEL_H40,
    MODEL_MIJIA_M40_S,
    MODEL_ROBOT_VACUUM_5,
    MODEL_S20_PLUS,
    MODEL_S40,
    MODEL_S40_PRO,
    MODEL_S40C,
    MODEL_X20_MAX,
    MODEL_X20_PRO,
)

_SPECS = Path(__file__).parent / "specs"
_PROPERTY_TEXT = {
    MODEL_S20_PLUS: {
        "STATE": "Status",
        "ERROR": "Device Fault",
        "CLEANING_MODE": "Sweep Mop Type",
        "TASK_STATUS": "Sweep Type",
        "CLEANED_AREA": "Cleaning Area",
        "CLEANING_TIME": "Cleaning Time",
        "SUCTION_LEVEL": "Suction Level",
        "WATER_VOLUME": "Mop Water Output Level",
        "CARPET_CLEANING": "Carpet Cleaning Method",
        "BATTERY_LEVEL": "Battery Level",
        "CHARGING_STATUS": "Charging State",
        "VOLUME": "Volume",
        "CHILD_LOCK": "Physical Control Locked",
        "WATER_TANK": "mop-status",
        "DND": "dnd-switch",
        "SCHEDULE": "order-clean",
        "CARPET_BOOST": "carpet-boost",
        "RELOCATION_STATUS": "status-extend",
        "RESUME_CLEANING": "sweep-break-switch",
        "FAULTS": "fault-index",
        "MAIN_BRUSH_TIME_LEFT": "Brush Left Time",
        "MAIN_BRUSH_LEFT": "Brush Life Level",
        "SIDE_BRUSH_TIME_LEFT": "Brush Left Time",
        "SIDE_BRUSH_LEFT": "Brush Life Level",
        "FILTER_TIME_LEFT": "Filter Left Time",
        "FILTER_LEFT": "Filter Life Level",
        "MOP_PAD_TIME_LEFT": "Brush Left Time",
        "MOP_PAD_LEFT": "Brush Life Level",
    },
    MODEL_X20_MAX: {
        "STATE": "Status",
        "ERROR": "Device Fault",
        "CLEANING_MODE": "Sweep Mop Type",
        "TASK_STATUS": "Sweep Type",
        "CLEANED_AREA": "Cleaning Area",
        "CLEANING_TIME": "Cleaning Time",
        "SUCTION_LEVEL": "Mode",
        "WATER_VOLUME": "Mop Water Output Level",
        "WATER_TANK": "Mop Status",
        "SCHEDULE": "Order Clean",
        "CARPET_BOOST": "Carpet Boost",
        "RESUME_CLEANING": "Sweep Break Switch",
        "RELOCATION_STATUS": "Location Status",
        "AUTO_DUST_COLLECTING": "Auto Dust Arrest",
        "AUTO_EMPTY_FREQUENCY": "Dust Arrest Frequency",
        "CLEANING_PROPERTIES": "Current Cleaning Config",
        "FAULTS": "Fault Ids",
        "CARPET_CLEANING": "Carpet Cleaning Method",
        "BATTERY_LEVEL": "Battery Level",
        "CHARGING_STATUS": "Charging State",
        "VOLUME": "Volume",
        "CHILD_LOCK": "Physical Control Locked",
        "MOP_PAD_LEFT": "Mop Life Level",
        "MOP_PAD_TIME_LEFT": "Mop Left Time",
        "DND": "No Disturb",
        "MAIN_BRUSH_LEFT": "Brush Life Level",
        "MAIN_BRUSH_TIME_LEFT": "Brush Left Time",
        "SIDE_BRUSH_LEFT": "Brush Life Level",
        "SIDE_BRUSH_TIME_LEFT": "Brush Left Time",
        "FILTER_LEFT": "Filter Life Level",
        "FILTER_TIME_LEFT": "Filter Left Time",
        "DETERGENT_LEFT": "Detergent Left Level",
    },
    MODEL_ROBOT_VACUUM_5: {
        "STATE": "Status",
        "ERROR": "Device Fault",
        "CLEANING_MODE": "Sweep Mop Type",
        "TASK_STATUS": "Sweep Type",
        "CLEANED_AREA": "Cleaning Area",
        "CLEANING_TIME": "Cleaning Time",
        "SUCTION_LEVEL": "Mode",
        "WATER_VOLUME": "Mop Water Output Level",
        "WATER_TANK": "Mop Status",
        "SCHEDULE": "Order Clean",
        "CARPET_BOOST": "Carpet Boost",
        "RESUME_CLEANING": "Sweep Break Switch",
        "RELOCATION_STATUS": "Location Status",
        "AUTO_DUST_COLLECTING": "Auto Dust Arrest",
        "AUTO_EMPTY_FREQUENCY": "Dust Arrest Frequency",
        "CLEANING_PROPERTIES": "Current Cleaning Config",
        "FAULTS": "Fault Ids",
        "CARPET_CLEANING": "Carpet Cleaning Method",
        "TOTAL_CLEANED_AREA": "Statistical Clean Area",
        "CLEANING_COUNT": "Statistical Cleaning Times",
        "TOTAL_CLEANING_TIME": "Statistical Cleaning Duration",
        "BATTERY_LEVEL": "Battery Level",
        "CHARGING_STATUS": "Charging State",
        "VOLUME": "Volume",
        "CHILD_LOCK": "Physical Control Locked",
        "MOP_PAD_LEFT": "Mop Life Level",
        "MOP_PAD_TIME_LEFT": "Mop Left Time",
        "DND": "No Disturb",
        "MAIN_BRUSH_LEFT": "Brush Life Level",
        "MAIN_BRUSH_TIME_LEFT": "Brush Left Time",
        "SIDE_BRUSH_LEFT": "Brush Life Level",
        "SIDE_BRUSH_TIME_LEFT": "Brush Left Time",
        "FILTER_LEFT": "Filter Life Level",
        "FILTER_TIME_LEFT": "Filter Left Time",
        "DETERGENT_LEFT": "Detergent Left Level",
        "DETERGENT_TIME_LEFT": "Detergent Left Time",
    },
    MODEL_S40_PRO: {
        "STATE": "Status",
        "ERROR": "Device Fault",
        "CLEANING_MODE": "Sweep Mop Type",
        "TASK_STATUS": "Sweep Type",
        "CLEANED_AREA": "Cleaning Area",
        "CLEANING_TIME": "Cleaning Time",
        "SUCTION_LEVEL": "Mode",
        "WATER_VOLUME": "Mop Water Output Level",
        "WATER_TANK": "Mop Status",
        "SCHEDULE": "Order Clean",
        "CARPET_BOOST": "Carpet Boost",
        "RESUME_CLEANING": "Sweep Break Switch",
        "RELOCATION_STATUS": "Location Status",
        "AUTO_DUST_COLLECTING": "Auto Dust Arrest",
        "AUTO_EMPTY_FREQUENCY": "Dust Arrest Frequency",
        "CLEANING_PROPERTIES": "Current Cleaning Config",
        "FAULTS": "Fault Ids",
        "CARPET_CLEANING": "Carpet Cleaning Method",
        "TOTAL_CLEANED_AREA": "Statistical Clean Area",
        "CLEANING_COUNT": "Statistical Cleaning Times",
        "TOTAL_CLEANING_TIME": "Statistical Cleaning Duration",
        "BATTERY_LEVEL": "Battery Level",
        "CHARGING_STATUS": "Charging State",
        "VOLUME": "Volume",
        "CHILD_LOCK": "Physical Control Locked",
        "MOP_PAD_LEFT": "Mop Life Level",
        "MOP_PAD_TIME_LEFT": "Mop Left Time",
        "DND": "No Disturb",
        "MAIN_BRUSH_LEFT": "Brush Life Level",
        "MAIN_BRUSH_TIME_LEFT": "Brush Left Time",
        "SIDE_BRUSH_LEFT": "Brush Life Level",
        "SIDE_BRUSH_TIME_LEFT": "Brush Left Time",
        "FILTER_LEFT": "Filter Life Level",
        "FILTER_TIME_LEFT": "Filter Left Time",
    },
}
_ACTION_TEXT = {
    MODEL_S20_PLUS: {
        "START": "Start Sweep",
        "STOP": "Stop Sweeping",
        "PAUSE": "Pause Sweeping",
        "RESUME": "continue-sweep",
        "CHARGE": "Start Charge",
        "LOCATE": "find-vacuum",
        "START_CUSTOM": "start-custom-sweep",
        "RESET_MAIN_BRUSH": "Reset Brush Life",
        "RESET_SIDE_BRUSH": "Reset Brush Life",
        "RESET_FILTER": "Reset Filter Life",
        "RESET_MOP_PAD": "Reset Brush Life",
    },
    MODEL_X20_MAX: {
        "START": "Start Sweep",
        "STOP": "Stop Sweeping",
        "PAUSE": "Pause Sweeping",
        "RESUME": "Continue Sweep",
        "START_CUSTOM": "Start Custom Sweep",
        "START_AUTO_EMPTY": "Start Dust Arrest",
        "CHARGE": "Start Charge",
        "LOCATE": "Identify",
        "RESET_MOP_PAD": "Reset Mop Life",
        "RESET_MAIN_BRUSH": "Reset Brush Life",
        "RESET_SIDE_BRUSH": "Reset Brush Life",
        "RESET_FILTER": "Reset Filter Life",
        "RESET_DETERGENT": "Reset Detergent Management Level",
    },
    MODEL_ROBOT_VACUUM_5: {
        "START": "Start Sweep",
        "STOP": "Stop Sweeping",
        "PAUSE": "Pause Sweeping",
        "RESUME": "Continue Sweep",
        "START_CUSTOM": "Start Custom Sweep",
        "START_AUTO_EMPTY": "Start Dust Arrest",
        "CHARGE": "Start Charge",
        "LOCATE": "Identify",
        "RESET_MOP_PAD": "Reset Mop Life",
        "RESET_MAIN_BRUSH": "Reset Brush Life",
        "RESET_SIDE_BRUSH": "Reset Brush Life",
        "RESET_FILTER": "Reset Filter Life",
        "RESET_DETERGENT": "Reset Detergent Management Level",
    },
    MODEL_S40_PRO: {
        "START": "Start Sweep",
        "STOP": "Stop Sweeping",
        "PAUSE": "Pause Sweeping",
        "RESUME": "Continue Sweep",
        "START_CUSTOM": "Start Custom Sweep",
        "START_AUTO_EMPTY": "Start Dust Arrest",
        "CHARGE": "Start Charge",
        "LOCATE": "Identify",
        "RESET_MOP_PAD": "Reset Mop Life",
        "RESET_MAIN_BRUSH": "Reset Brush Life",
        "RESET_SIDE_BRUSH": "Reset Brush Life",
        "RESET_FILTER": "Reset Filter Life",
    },
}
_PROPERTY_TEXT[MODEL_X20_PRO] = _PROPERTY_TEXT[MODEL_X20_MAX]
_ACTION_TEXT[MODEL_X20_PRO] = _ACTION_TEXT[MODEL_X20_MAX]
_PROPERTY_TEXT[MODEL_S40] = _PROPERTY_TEXT[MODEL_ROBOT_VACUUM_5]
_ACTION_TEXT[MODEL_S40] = _ACTION_TEXT[MODEL_ROBOT_VACUUM_5]
_PROPERTY_TEXT[MODEL_H40] = _PROPERTY_TEXT[MODEL_S40]
_ACTION_TEXT[MODEL_H40] = _ACTION_TEXT[MODEL_S40]
_PROPERTY_TEXT[MODEL_S40C] = _PROPERTY_TEXT[MODEL_S40]
_ACTION_TEXT[MODEL_S40C] = _ACTION_TEXT[MODEL_S40]
_PROPERTY_TEXT[MODEL_H50_PRO] = _PROPERTY_TEXT[MODEL_S40]
_ACTION_TEXT[MODEL_H50_PRO] = _ACTION_TEXT[MODEL_S40]
_PROPERTY_TEXT[MODEL_H50] = _PROPERTY_TEXT[MODEL_S40]
_ACTION_TEXT[MODEL_H50] = _ACTION_TEXT[MODEL_S40]
_PROPERTY_TEXT[MODEL_ROBOT_VACUUM_5_PRO] = _PROPERTY_TEXT[MODEL_S40]
_ACTION_TEXT[MODEL_ROBOT_VACUUM_5_PRO] = _ACTION_TEXT[MODEL_S40]
_PROPERTY_TEXT[MODEL_ROBOT_VACUUM_6_MAX] = {
    name: text
    for name, text in _PROPERTY_TEXT[MODEL_ROBOT_VACUUM_5].items()
    if name != "CLEANING_MODE"
}
_ACTION_TEXT[MODEL_ROBOT_VACUUM_6_MAX] = _ACTION_TEXT[MODEL_ROBOT_VACUUM_5]
_PROPERTY_TEXT[MODEL_ROBOT_VACUUM_6_PRO] = {
    name: text
    for name, text in _PROPERTY_TEXT[MODEL_ROBOT_VACUUM_6_MAX].items()
    if name not in {"MOP_PAD_LEFT", "MOP_PAD_TIME_LEFT"}
}
_ACTION_TEXT[MODEL_ROBOT_VACUUM_6_PRO] = {
    name: text
    for name, text in _ACTION_TEXT[MODEL_ROBOT_VACUUM_6_MAX].items()
    if name != "RESET_MOP_PAD"
}
_PROPERTY_TEXT[MODEL_S60_PLUS] = _PROPERTY_TEXT[MODEL_S40_PRO]
_ACTION_TEXT[MODEL_S60_PLUS] = _ACTION_TEXT[MODEL_S40_PRO]
_PROPERTY_TEXT[MODEL_S60] = {
    name: text
    for name, text in _PROPERTY_TEXT[MODEL_S60_PLUS].items()
    if name not in {"AUTO_DUST_COLLECTING", "AUTO_EMPTY_FREQUENCY"}
}
_ACTION_TEXT[MODEL_S60] = {
    name: text
    for name, text in _ACTION_TEXT[MODEL_S60_PLUS].items()
    if name != "START_AUTO_EMPTY"
}
_PROPERTY_TEXT[MODEL_ROBOT_VACUUM_6] = {
    name: text
    for name, text in _PROPERTY_TEXT[MODEL_S40_PRO].items()
    if name not in {"CLEANING_MODE", "MOP_PAD_LEFT", "MOP_PAD_TIME_LEFT"}
}
_ACTION_TEXT[MODEL_ROBOT_VACUUM_6] = {
    name: text
    for name, text in _ACTION_TEXT[MODEL_S40_PRO].items()
    if name != "RESET_MOP_PAD"
}
_PROPERTY_TEXT[MODEL_H50_PRO_ROLLER] = _PROPERTY_TEXT[MODEL_ROBOT_VACUUM_6]
_ACTION_TEXT[MODEL_H50_PRO_ROLLER] = _ACTION_TEXT[MODEL_ROBOT_VACUUM_6]
_PROPERTY_TEXT[MODEL_MIJIA_ROBOT_VACUUM_6] = _PROPERTY_TEXT[MODEL_ROBOT_VACUUM_6]
_ACTION_TEXT[MODEL_MIJIA_ROBOT_VACUUM_6] = _ACTION_TEXT[MODEL_ROBOT_VACUUM_6]
_PROPERTY_TEXT[MODEL_MIJIA_7C] = _PROPERTY_TEXT[MODEL_H50_PRO_ROLLER]
_ACTION_TEXT[MODEL_MIJIA_7C] = _ACTION_TEXT[MODEL_H50_PRO_ROLLER]
_PROPERTY_TEXT[MODEL_MIJIA_M40_S] = _PROPERTY_TEXT[MODEL_ROBOT_VACUUM_5]
_ACTION_TEXT[MODEL_MIJIA_M40_S] = _ACTION_TEXT[MODEL_ROBOT_VACUUM_5]
_PROPERTY_TEXT[MODEL_MIJIA_5_PRO] = _PROPERTY_TEXT[MODEL_ROBOT_VACUUM_5_PRO]
_ACTION_TEXT[MODEL_MIJIA_5_PRO] = _ACTION_TEXT[MODEL_ROBOT_VACUUM_5_PRO]
_PROPERTY_TEXT[MODEL_MIJIA_5C] = _PROPERTY_TEXT[MODEL_H50_PRO]
_ACTION_TEXT[MODEL_MIJIA_5C] = _ACTION_TEXT[MODEL_H50_PRO]
_PROPERTY_TEXT[MODEL_MIJIA_M30] = _PROPERTY_TEXT[MODEL_X20_PRO]
_ACTION_TEXT[MODEL_MIJIA_M30] = _ACTION_TEXT[MODEL_X20_PRO]
_PROPERTY_TEXT[MODEL_MIJIA_6_MAX] = _PROPERTY_TEXT[MODEL_ROBOT_VACUUM_6_MAX]
_ACTION_TEXT[MODEL_MIJIA_6_MAX] = _ACTION_TEXT[MODEL_ROBOT_VACUUM_6_MAX]
_PROPERTY_TEXT[MODEL_MIJIA_6_PRO] = _PROPERTY_TEXT[MODEL_ROBOT_VACUUM_6_PRO]
_ACTION_TEXT[MODEL_MIJIA_6_PRO] = _ACTION_TEXT[MODEL_ROBOT_VACUUM_6_PRO]
_PROPERTY_TEXT[MODEL_MIJIA_ROBOT_VACUUM_5] = _PROPERTY_TEXT[MODEL_H50_PRO]
_ACTION_TEXT[MODEL_MIJIA_ROBOT_VACUUM_5] = _ACTION_TEXT[MODEL_H50_PRO]
_PROPERTY_TEXT[MODEL_MIJIA_M30_PRO] = {
    **_PROPERTY_TEXT[MODEL_MIJIA_M30],
    "DETERGENT_TIME_LEFT": "Detergent Left Time",
}
_ACTION_TEXT[MODEL_MIJIA_M30_PRO] = _ACTION_TEXT[MODEL_MIJIA_M30]
_PROPERTY_TEXT[MODEL_MIJIA_ROBOT_VACUUM_4] = _PROPERTY_TEXT[MODEL_S60]
_ACTION_TEXT[MODEL_MIJIA_ROBOT_VACUUM_4] = _ACTION_TEXT[MODEL_S60]
_PROPERTY_TEXT[MODEL_MIJIA_H40] = {
    name: text
    for name, text in _PROPERTY_TEXT[MODEL_X20_PRO].items()
    if name not in {"AUTO_DUST_COLLECTING", "AUTO_EMPTY_FREQUENCY", "DETERGENT_LEFT"}
}
_ACTION_TEXT[MODEL_MIJIA_H40] = {
    name: text
    for name, text in _ACTION_TEXT[MODEL_X20_PRO].items()
    if name not in {"RESET_DETERGENT", "START_AUTO_EMPTY"}
}
_PROPERTY_TEXT[MODEL_MIJIA_7_MAX] = {
    name: text
    for name, text in _PROPERTY_TEXT[MODEL_ROBOT_VACUUM_6_MAX].items()
    if name != "DETERGENT_TIME_LEFT"
}
_ACTION_TEXT[MODEL_MIJIA_7_MAX] = {
    name: text
    for name, text in _ACTION_TEXT[MODEL_ROBOT_VACUUM_6_MAX].items()
    if name != "START_CUSTOM"
}
_PROPERTY_TEXT[MODEL_H50_ROLLER] = {
    **_PROPERTY_TEXT[MODEL_ROBOT_VACUUM_6],
    "CLEANING_MODE": "Sweep Mop Type",
}
_ACTION_TEXT[MODEL_H50_ROLLER] = _ACTION_TEXT[MODEL_ROBOT_VACUUM_6]
_SWEEP_PROPERTY_TEXT = {
    "STATE": "Status",
    "ERROR": "Device Fault",
    "BATTERY_LEVEL": "Battery Level",
    "SIDE_BRUSH_LEFT": "",
    "SIDE_BRUSH_TIME_LEFT": "",
    "MAIN_BRUSH_LEFT": "",
    "MAIN_BRUSH_TIME_LEFT": "",
    "FILTER_LEFT": "",
    "FILTER_TIME_LEFT": "",
    "MOP_PAD_LEFT": "",
    "MOP_PAD_TIME_LEFT": "",
    "CLEANING_TIME": "",
    "CLEANED_AREA": "",
}
_PROPERTY_TEXT[MODEL_E10] = _SWEEP_PROPERTY_TEXT
_PROPERTY_TEXT[MODEL_E12] = _SWEEP_PROPERTY_TEXT
_PROPERTY_TEXT[MODEL_E10C] = _SWEEP_PROPERTY_TEXT
_SWEEP_ACTION_TEXT = {
    "START": "Start Sweep",
    "STOP": "Stop Sweeping",
    "CHARGE": "Start Charge",
}
_ACTION_TEXT[MODEL_E10] = _SWEEP_ACTION_TEXT
_ACTION_TEXT[MODEL_E12] = _SWEEP_ACTION_TEXT
_ACTION_TEXT[MODEL_E10C] = _SWEEP_ACTION_TEXT
_PROPERTY_TEXT[MODEL_S20] = _SWEEP_PROPERTY_TEXT
_ACTION_TEXT[MODEL_S20] = _SWEEP_ACTION_TEXT
_PROPERTY_TEXT[MODEL_X20] = _SWEEP_PROPERTY_TEXT
_ACTION_TEXT[MODEL_X20] = _SWEEP_ACTION_TEXT
_PROPERTY_TEXT[MODEL_S12] = _SWEEP_PROPERTY_TEXT
_ACTION_TEXT[MODEL_S12] = _SWEEP_ACTION_TEXT
_PROPERTY_TEXT[MODEL_T12] = _SWEEP_PROPERTY_TEXT
_ACTION_TEXT[MODEL_T12] = _SWEEP_ACTION_TEXT
_PROPERTY_TEXT[MODEL_MIJIA_SWEEP_MOP_3] = {
    **_SWEEP_PROPERTY_TEXT,
    "CLEANING_TIME": "cleaning-time",
}
_ACTION_TEXT[MODEL_MIJIA_SWEEP_MOP_3] = _SWEEP_ACTION_TEXT
_PROPERTY_TEXT[MODEL_MIJIA_SWEEP_MOP_2] = _PROPERTY_TEXT[MODEL_X20]
_ACTION_TEXT[MODEL_MIJIA_SWEEP_MOP_2] = _ACTION_TEXT[MODEL_X20]
_PROPERTY_TEXT[MODEL_MIJIA_3C] = _PROPERTY_TEXT[MODEL_S20]
_ACTION_TEXT[MODEL_MIJIA_3C] = _ACTION_TEXT[MODEL_S20]
_PROPERTY_TEXT[MODEL_E5] = {
    "STATE": "Status",
    "ERROR": "Device Fault",
    "BATTERY_LEVEL": "Battery Level",
    "FILTER_LEFT": "Filter Life Level",
    "SIDE_BRUSH_LEFT": "Brush Life Level",
    "TOTAL_CLEANING_TIME": "total-clean-time",
    "CLEANING_COUNT": "total-clean-count",
}
_ACTION_TEXT[MODEL_E5] = {
    "START": "Start Sweep",
    "STOP": "Stop Sweeping",
    "PAUSE": "Pause Sweeping",
    "RESUME": "Continue Sweep",
    "CHARGE": "Stop And Gocharge",
    "LOCATE": "Identify",
    "RESET_FILTER": "Reset Filter Life",
    "RESET_SIDE_BRUSH": "Reset Brush Life",
}
_SPEC_FILES = {
    MODEL_S20_PLUS: ("b108gl.json",),
    MODEL_X20_MAX: ("d109gl.json", "d109gl_v1.json"),
    MODEL_X20_PRO: ("d102gl.json",),
    MODEL_ROBOT_VACUUM_5: ("ov31gl.json", "ov31gl_v1.json"),
    MODEL_MIJIA_M40_S: ("ov31cn.json", "ov31cn_v1.json"),
    MODEL_S40_PRO: ("ov71gl.json",),
    MODEL_S40: ("ov81gl.json",),
    MODEL_H40: ("ov51gl.json",),
    MODEL_S40C: ("e101gb.json",),
    MODEL_H50_PRO: ("ov42gl.json", "ov42gl_v1.json"),
    MODEL_MIJIA_5C: ("ov42cn.json", "ov42cn_v1.json"),
    MODEL_H50: ("ov43gb.json", "ov43gb_v1.json"),
    MODEL_ROBOT_VACUUM_5_PRO: ("ov21gl.json", "ov21gl_v1.json"),
    MODEL_MIJIA_5_PRO: ("ov21cn.json", "ov21cn_v1.json"),
    MODEL_ROBOT_VACUUM_6: ("pv32gl.json", "pv32gl_v1.json"),
    MODEL_MIJIA_ROBOT_VACUUM_6: ("pv32cn.json", "pv32cn_v1.json"),
    MODEL_ROBOT_VACUUM_6_MAX: ("pv11gl.json",),
    MODEL_ROBOT_VACUUM_6_PRO: ("pv21gl.json",),
    MODEL_S60_PLUS: ("pv51gl.json",),
    MODEL_S60: ("pv81gl.json",),
    MODEL_H50_PRO_ROLLER: ("qv41gl.json",),
    MODEL_MIJIA_7C: ("qv41cn.json",),
    MODEL_H50_ROLLER: ("qv42gl.json",),
    MODEL_E10: ("b112.json",),
    MODEL_E12: ("b112gl.json",),
    MODEL_E10C: ("b112bk.json",),
    MODEL_E5: ("c108.json",),
    MODEL_S20: ("d106gl.json",),
    MODEL_X20: ("c101eu.json",),
    MODEL_S12: ("b106eu.json",),
    MODEL_T12: ("b106bk.json",),
    MODEL_MIJIA_SWEEP_MOP_3: ("c104.json",),
    MODEL_MIJIA_SWEEP_MOP_2: ("c101.json", "c101_v1.json"),
    MODEL_MIJIA_3C: ("c103.json", "c103_v1.json"),
    MODEL_MIJIA_M30: ("d102ev.json",),
    MODEL_MIJIA_6_MAX: ("pv11cn.json", "pv11cn_v1.json"),
    MODEL_MIJIA_6_PRO: ("pv21cn.json", "pv21cn_v1.json"),
    MODEL_MIJIA_7_MAX: ("qv12cn.json",),
    MODEL_MIJIA_ROBOT_VACUUM_5: ("pv31cn.json",),
    MODEL_MIJIA_M30_PRO: ("c107.json", "c107_v1.json"),
    MODEL_MIJIA_ROBOT_VACUUM_4: ("ov81cn.json", "ov81cn_v1.json"),
    MODEL_MIJIA_H40: ("d101.json", "d101_v1.json", "d101_v2.json"),
}
_ABSENT_PROPERTIES = (
    "STATUS",
    "OFF_PEAK_CHARGING",
    "DND_START",
    "DND_END",
    "MAP_DATA",
    "OBJECT_NAME",
    "OLD_MAP_DATA",
    "MAP_LIST",
    "MULTI_FLOOR_MAP",
    "MAP_SAVING",
    "SILVER_ION_LEFT",
    "SILVER_ION_TIME_LEFT",
    "AUTO_EMPTY_STATUS",
    "DUST_COLLECTION",
)
_ABSENT_ACTIONS = (
    "PLAY_SOUND",
    "BACKUP_MAP",
    "REQUEST_MAP",
    "UPDATE_MAP_DATA",
    "WIFI_MAP",
    "RESET_SILVER_ION",
)


class _Capability:
    loaded = False


class _Device:
    def __init__(self) -> None:
        self.property_mapping = None
        self.action_mapping = None
        self._property_codec = None
        self._map_manager = None
        self._protocol = type("Protocol", (), {"property_transport": None})()
        self.host = ""
        self.token = ""
        self.capability = _Capability()


def _load(name: str) -> tuple[dict[tuple[int, int], str], dict[tuple[int, int], str]]:
    document = json.loads((_SPECS / name).read_text(encoding="utf-8"))
    properties: dict[tuple[int, int], str] = {}
    actions: dict[tuple[int, int], str] = {}
    for service in document["services"]:
        siid = service["iid"]
        for prop in service.get("properties") or []:
            properties[(siid, prop["iid"])] = prop.get("description") or ""
        for action in service.get("actions") or []:
            actions[(siid, action["iid"])] = action.get("description") or ""
    return properties, actions


def _charging_value(name: str, number: int) -> str:
    document = json.loads((_SPECS / name).read_text(encoding="utf-8"))
    for service in document["services"]:
        if service["iid"] != 3:
            continue
        for prop in service["properties"]:
            if prop["iid"] == 2:
                for item in prop["value-list"]:
                    if item["value"] == number:
                        return item["description"]
    raise AssertionError(name)


def test_charging_value_three_is_not_chargeable():
    for name in (
        "b108gl.json",
        "d109gl.json",
        "d109gl_v1.json",
        "d102gl.json",
        "ov31gl.json",
        "ov31gl_v1.json",
        "ov71gl.json",
        "ov81gl.json",
        "ov51gl.json",
        "e101gb.json",
        "ov42gl.json",
        "ov42gl_v1.json",
        "ov43gb.json",
        "ov43gb_v1.json",
        "ov21gl.json",
        "ov21gl_v1.json",
        "pv32gl.json",
        "pv32gl_v1.json",
        "pv11gl.json",
        "pv21gl.json",
        "pv51gl.json",
        "pv81gl.json",
        "qv41gl.json",
        "qv42gl.json",
        "pv32cn.json",
        "pv32cn_v1.json",
        "qv41cn.json",
        "ov31cn.json",
        "ov31cn_v1.json",
        "ov21cn.json",
        "ov21cn_v1.json",
        "ov42cn.json",
        "ov42cn_v1.json",
        "d102ev.json",
        "pv11cn.json",
        "pv11cn_v1.json",
        "pv21cn.json",
        "pv21cn_v1.json",
        "qv12cn.json",
        "pv31cn.json",
        "c107.json",
        "c107_v1.json",
        "ov81cn.json",
        "ov81cn_v1.json",
        "d101.json",
        "d101_v1.json",
        "d101_v2.json",
    ):
        assert _charging_value(name, 3) == "Not Chargeable"
        assert _charging_value(name, 1) == "Charging"


def test_installed_addresses_match_the_spec_and_defaults_do_not_leak():
    for model, filenames in _SPEC_FILES.items():
        family = resolve_family(model)
        assert family is not None
        device = _Device()
        apply_family(device, family)
        assert set(device.property_mapping) == {
            DreameVacuumProperty[name] for name in _PROPERTY_TEXT[model]
        }
        assert set(device.action_mapping) == {
            DreameVacuumAction[name] for name in _ACTION_TEXT[model]
        }
        for prop in _ABSENT_PROPERTIES:
            assert DreameVacuumProperty[prop] not in device.property_mapping
        for action in _ABSENT_ACTIONS:
            assert DreameVacuumAction[action] not in device.action_mapping
        for filename in filenames:
            properties, actions = _load(filename)
            _assert_properties(device, properties, _PROPERTY_TEXT[model])
            _assert_actions(device, actions, _ACTION_TEXT[model])


def _assert_properties(
    device: _Device, spec: dict[tuple[int, int], str], expected: dict[str, str]
) -> None:
    owners = {
        (mapping["siid"], mapping["piid"]): prop.name
        for prop, mapping in device.property_mapping.items()
    }
    for prop, mapping in device.property_mapping.items():
        assert spec[(mapping["siid"], mapping["piid"])] == expected[prop.name]
    for prop, mapping in DreameVacuumPropertyMapping.items():
        pair = (mapping.get("siid"), mapping.get("piid"))
        if pair not in spec:
            continue
        owner = owners.get(pair)
        if owner is None:
            installed = device.property_mapping.get(prop)
            assert installed is None or (installed["siid"], installed["piid"]) != pair
            continue
        assert spec[pair] == expected[owner]


def _assert_actions(
    device: _Device, spec: dict[tuple[int, int], str], expected: dict[str, str]
) -> None:
    owners = {
        (mapping["siid"], mapping["aiid"]): action.name
        for action, mapping in device.action_mapping.items()
    }
    for action, mapping in device.action_mapping.items():
        assert spec[(mapping["siid"], mapping["aiid"])] == expected[action.name]
    for action, mapping in DreameVacuumActionMapping.items():
        pair = (mapping.get("siid"), mapping.get("aiid"))
        if pair not in spec:
            continue
        owner = owners.get(pair)
        if owner is None:
            installed = device.action_mapping.get(action)
            assert installed is None or (installed["siid"], installed["aiid"]) != pair
            continue
        assert spec[pair] == expected[owner]
