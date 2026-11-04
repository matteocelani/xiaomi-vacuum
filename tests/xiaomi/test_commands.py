"""Command routing for S20+ and X20 Max stays on the mapped action."""

from __future__ import annotations

from custom_components.dreame_vacuum.dreame.device import (
    DreameVacuumDevice,
    DreameVacuumDeviceInfo,
)
from custom_components.dreame_vacuum.dreame.exceptions import InvalidActionException
from custom_components.dreame_vacuum.dreame.map import DreameMapVacuumMapManager
from custom_components.dreame_vacuum.dreame.types import (
    DreameVacuumAction,
    DreameVacuumProperty,
    DreameVacuumState,
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
    MODEL_MIJIA_SWEEP_MOP_2S,
    MODEL_MIJIA_SWEEP_MOP_3S,
    MODEL_MIJIA_SWEEP_MOP_3S_ZH,
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
    MODEL_X20_PRO,
    resolve_family,
)
from custom_components.dreame_vacuum.xiaomi.mapping import (
    MODEL_H40,
    MODEL_ROBOT_VACUUM_5,
    MODEL_S20_PLUS,
    MODEL_S40,
    MODEL_S40_PRO,
    MODEL_S40C,
    MODEL_X20_MAX,
)
import pytest
from tests.xiaomi.helpers import release_device

_TOKEN = "00" * 16
_MAC = "00:00:00:00:00:00"


def _device(model: str) -> tuple[DreameVacuumDevice, list[tuple[int, int]]]:
    device = DreameVacuumDevice(
        "Sim",
        "127.0.0.1",
        _TOKEN,
        _MAC,
        family_resolver=resolve_family,
    )
    device.host = ""
    device.info = DreameVacuumDeviceInfo(
        {
            "model": model,
            "fw_ver": "1.0_1",
            "mac": _MAC,
            "netif": {"localIp": "127.0.0.1"},
        }
    )
    device._apply_reported_family()
    sent: list[tuple[int, int]] = []

    def action(
        siid: int, aiid: int, parameters: object = None, retry_count: int = 2
    ) -> dict[str, int]:
        del parameters, retry_count
        sent.append((siid, aiid))
        return {"code": 0}

    def set_property(
        siid: int, piid: int, value: object = None, retry_count: int = 2
    ) -> list[dict[str, int]]:
        del siid, piid, value, retry_count
        return [{"code": 0}]

    device._protocol.action = action
    device._protocol.set_property = set_property
    return device, sent


def test_paused_start_uses_continue_sweep_and_skips_unmapped_actions():
    expected = {
        MODEL_S20_PLUS: {
            "resume": (6, 1),
            "start": (2, 1),
            "pause": (2, 6),
            "charge": (3, 1),
        },
        MODEL_MIJIA_SWEEP_MOP_2S: {
            "resume": (6, 1),
            "start": (2, 1),
            "pause": (2, 6),
            "charge": (3, 1),
        },
        MODEL_MIJIA_SWEEP_MOP_3S: {
            "resume": (6, 1),
            "start": (2, 1),
            "pause": (2, 6),
            "charge": (3, 1),
        },
        MODEL_MIJIA_SWEEP_MOP_3S_ZH: {
            "resume": (6, 1),
            "start": (2, 1),
            "pause": (2, 6),
            "charge": (3, 1),
        },
        MODEL_X20_MAX: {
            "resume": (2, 8),
            "start": (2, 1),
            "pause": (2, 7),
            "charge": (3, 1),
        },
        MODEL_X20_PRO: {
            "resume": (2, 8),
            "start": (2, 1),
            "pause": (2, 7),
            "charge": (3, 1),
        },
        MODEL_ROBOT_VACUUM_5: {
            "resume": (2, 8),
            "start": (2, 1),
            "pause": (2, 7),
            "charge": (3, 1),
        },
        MODEL_S40_PRO: {
            "resume": (2, 8),
            "start": (2, 1),
            "pause": (2, 7),
            "charge": (3, 1),
        },
        MODEL_S40: {
            "resume": (2, 8),
            "start": (2, 1),
            "pause": (2, 7),
            "charge": (3, 1),
        },
        MODEL_H40: {
            "resume": (2, 8),
            "start": (2, 1),
            "pause": (2, 7),
            "charge": (3, 1),
        },
        MODEL_H50_PRO: {
            "resume": (2, 8),
            "start": (2, 1),
            "pause": (2, 7),
            "charge": (3, 1),
        },
        MODEL_H50_PRO_ROLLER: {
            "resume": (2, 8),
            "start": (2, 1),
            "pause": (2, 7),
            "charge": (3, 1),
        },
        MODEL_H50_ROLLER: {
            "resume": (2, 8),
            "start": (2, 1),
            "pause": (2, 7),
            "charge": (3, 1),
        },
        MODEL_H50: {
            "resume": (2, 8),
            "start": (2, 1),
            "pause": (2, 7),
            "charge": (3, 1),
        },
        MODEL_S40C: {
            "resume": (2, 8),
            "start": (2, 1),
            "pause": (2, 7),
            "charge": (3, 1),
        },
        MODEL_ROBOT_VACUUM_5_PRO: {
            "resume": (2, 8),
            "start": (2, 1),
            "pause": (2, 7),
            "charge": (3, 1),
        },
        MODEL_ROBOT_VACUUM_6: {
            "resume": (2, 8),
            "start": (2, 1),
            "pause": (2, 7),
            "charge": (3, 1),
        },
        MODEL_ROBOT_VACUUM_6_MAX: {
            "resume": (2, 8),
            "start": (2, 1),
            "pause": (2, 7),
            "charge": (3, 1),
        },
        MODEL_ROBOT_VACUUM_6_PRO: {
            "resume": (2, 8),
            "start": (2, 1),
            "pause": (2, 7),
            "charge": (3, 1),
        },
        MODEL_S60_PLUS: {
            "resume": (2, 8),
            "start": (2, 1),
            "pause": (2, 7),
            "charge": (3, 1),
        },
        MODEL_S60: {
            "resume": (2, 8),
            "start": (2, 1),
            "pause": (2, 7),
            "charge": (3, 1),
        },
    }
    for model, addresses in expected.items():
        device, sent = _device(model)
        try:
            device.data[DreameVacuumProperty.STATE.value] = int(
                DreameVacuumState.PAUSED
            )
            device.start()
            assert sent[-1] == addresses["resume"]
            device.data[DreameVacuumProperty.STATE.value] = int(
                DreameVacuumState.SWEEPING
            )
            device.pause()
            assert sent[-1] == addresses["pause"]
            device.data[DreameVacuumProperty.STATE.value] = int(DreameVacuumState.IDLE)
            device.start()
            assert sent[-1] == addresses["start"]
            device.return_to_base()
            assert sent[-1] == addresses["charge"]
            device.set_volume(40)
            forbidden = {
                device.action_mapping[item]
                for item in (
                    DreameVacuumAction.PLAY_SOUND,
                    DreameVacuumAction.BACKUP_MAP,
                    DreameVacuumAction.REQUEST_MAP,
                    DreameVacuumAction.RESET_SILVER_ION,
                )
                if item in device.action_mapping
            }
            assert not forbidden
            for siid, aiid in sent:
                assert (siid, aiid) in set(addresses.values())
            with pytest.raises(InvalidActionException):
                device.call_action(DreameVacuumAction.PLAY_SOUND)
            assert sent[-1] == addresses["charge"]
            manager = DreameMapVacuumMapManager.__new__(DreameMapVacuumMapManager)
            manager.action_mapping = device.action_mapping
            assert manager._mapped_action(DreameVacuumAction.REQUEST_MAP) is None
            assert manager._mapped_action(DreameVacuumAction.UPDATE_MAP_DATA) is None
            manager.action_mapping = None
            dreame_map = manager._mapped_action(DreameVacuumAction.REQUEST_MAP)
            assert dreame_map is not None
            assert dreame_map["siid"] == 6
        finally:
            release_device(device)


def test_property_reads_stay_inside_the_explicit_map():
    for model in (
        MODEL_S20_PLUS,
        MODEL_MIJIA_SWEEP_MOP_2S,
        MODEL_MIJIA_SWEEP_MOP_3S,
        MODEL_MIJIA_SWEEP_MOP_3S_ZH,
        MODEL_X20_MAX,
        MODEL_X20_PRO,
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
        MODEL_S60_PLUS,
        MODEL_S60,
        MODEL_H50_PRO_ROLLER,
        MODEL_H50_ROLLER,
        MODEL_E10,
        MODEL_E12,
        MODEL_E10C,
        MODEL_E5,
        MODEL_S20,
        MODEL_X20,
        MODEL_S12,
        MODEL_T12,
    ):
        device, _sent = _device(model)
        requested: list[tuple[int, int]] = []

        def get_properties(
            parameters: list[dict[str, int]],
            retry_count: int = 1,
            timeout: object = None,
            requested: list[tuple[int, int]] = requested,
        ) -> list[dict[str, object]]:
            del retry_count, timeout
            requested.extend((item["siid"], item["piid"]) for item in parameters)
            return [
                {
                    "did": item["did"],
                    "siid": item["siid"],
                    "piid": item["piid"],
                    "code": 0,
                    "value": 0,
                }
                for item in parameters
            ]

        device._protocol.get_properties = get_properties
        device._request_properties()
        allowed = {
            (mapping["siid"], mapping["piid"])
            for mapping in device.property_mapping.values()
        }
        controls = {
            (control.siid, control.piid)
            for control in device._property_codec.controls
            if control.siid is not None and control.piid is not None
        }
        assert requested
        assert set(requested) <= allowed | controls
        if model != MODEL_E5:
            assert (7, 2) not in requested
        if model == MODEL_S20_PLUS:
            assert (2, 20) in requested
        if model in (
            MODEL_MIJIA_SWEEP_MOP_2S,
            MODEL_MIJIA_SWEEP_MOP_3S,
            MODEL_MIJIA_SWEEP_MOP_3S_ZH,
        ):
            assert (2, 20) not in requested
        if model in (
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
            MODEL_H50_PRO_ROLLER,
            MODEL_H50_ROLLER,
        ):
            assert (4, 1) in requested
            assert (5, 2) in requested
        if model == MODEL_S40_PRO:
            assert (18, 1) not in requested
            assert (19, 1) not in requested
        if model in (
            MODEL_S40,
            MODEL_H40,
            MODEL_H50,
            MODEL_H50_PRO,
            MODEL_S40C,
            MODEL_ROBOT_VACUUM_5_PRO,
        ):
            assert (18, 1) in requested
            assert (19, 1) in requested
        if model == MODEL_ROBOT_VACUUM_6:
            assert (9, 1) not in requested
            assert (18, 1) not in requested
            assert (19, 1) in requested
            assert (24, 1) in requested
        if model in (MODEL_H50_PRO_ROLLER, MODEL_H50_ROLLER):
            assert (9, 1) not in requested
            assert (18, 1) not in requested
            assert (19, 1) in requested
            assert (24, 1) in requested
        if model == MODEL_ROBOT_VACUUM_6_MAX:
            assert (9, 1) in requested
            assert (18, 1) in requested
            assert (19, 1) in requested
            assert (24, 1) in requested
            assert (2, 107) in requested
        if model == MODEL_ROBOT_VACUUM_6_PRO:
            assert (9, 1) not in requested
            assert (18, 1) in requested
            assert (19, 1) in requested
            assert (24, 1) in requested
            assert (2, 107) in requested
        if model == MODEL_S60_PLUS:
            assert (4, 1) in requested
            assert (5, 2) in requested
            assert (9, 1) in requested
            assert (18, 1) not in requested
            assert (19, 1) in requested
            assert (2, 32) in requested
            assert (2, 109) in requested
            assert (24, 1) not in requested
        if model == MODEL_S60:
            assert (4, 1) in requested
            assert (5, 2) in requested
            assert (9, 1) in requested
            assert (18, 1) not in requested
            assert (19, 1) not in requested
            assert (2, 32) not in requested
            assert (2, 109) in requested
            assert (24, 1) not in requested
        if model in (MODEL_E10, MODEL_E12, MODEL_E10C):
            assert (4, 1) in requested
            assert (4, 2) in requested
            assert (2, 8) in requested
            assert (7, 5) in requested
            assert (12, 1) in requested
            assert (2, 9) not in requested
        if model == MODEL_S20:
            assert (4, 1) in requested
            assert (4, 2) in requested
            assert (2, 8) in requested
            assert (2, 11) in requested
            assert (7, 5) in requested
            assert (7, 35) in requested
            assert (7, 48) in requested
            assert (7, 50) in requested
            assert (12, 1) in requested
            assert (2, 9) not in requested
            assert (15, 1) not in requested
            assert (16, 1) not in requested
            assert (18, 1) not in requested
        if model in (MODEL_S12, MODEL_T12):
            assert (4, 1) in requested
            assert (4, 2) in requested
            assert (2, 8) in requested
            assert (7, 5) in requested
            assert (7, 35) in requested
            assert (7, 48) in requested
            assert (7, 50) in requested
            assert (12, 1) in requested
            assert (2, 9) not in requested
            assert (2, 11) not in requested
            assert (7, 47) not in requested
            assert (7, 49) not in requested
            assert (7, 55) not in requested
        if model == MODEL_X20:
            assert (4, 1) in requested
            assert (4, 2) in requested
            assert (2, 8) in requested
            assert (7, 5) in requested
            assert (7, 35) in requested
            assert (7, 54) in requested
            assert (7, 59) in requested
            assert (7, 60) in requested
            assert (12, 1) in requested
            assert (2, 9) not in requested
            assert (2, 11) not in requested
            assert (7, 62) not in requested
            assert (7, 63) not in requested
            assert (15, 1) not in requested
        if model == MODEL_E5:
            assert (2, 4) in requested
            assert (2, 5) in requested
            assert (2, 12) in requested
            assert (3, 2) in requested
            assert (6, 2) in requested
            assert (7, 2) in requested
            assert (10, 1) in requested
            assert (14, 1) in requested
            assert (2, 11) not in requested
            assert (13, 1) not in requested
            assert (15, 1) not in requested
        if model == MODEL_X20_PRO:
            assert (4, 1) in requested
            assert (5, 2) in requested
            assert (18, 1) in requested
            assert (19, 1) in requested
            assert (2, 85) not in requested
            assert (9, 1) in requested
        if model not in (
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
            MODEL_S60_PLUS,
            MODEL_S60,
            MODEL_X20_PRO,
            MODEL_H50_PRO_ROLLER,
            MODEL_H50_ROLLER,
            MODEL_E10,
            MODEL_E12,
            MODEL_E10C,
            MODEL_E5,
            MODEL_S20,
            MODEL_X20,
            MODEL_S12,
            MODEL_T12,
        ):
            assert controls == set()
            assert (4, 1) not in requested
            assert (5, 2) not in requested


def test_sweep_family_commands_stay_on_start_stop_and_charge():
    """Pause and locate are not in the spec, so they are not sent."""
    for model in (
        MODEL_E10,
        MODEL_E12,
        MODEL_E10C,
        MODEL_S20,
        MODEL_X20,
        MODEL_S12,
        MODEL_T12,
    ):
        device, sent = _device(model)
        try:
            device.data[DreameVacuumProperty.STATE.value] = int(
                DreameVacuumState.PAUSED
            )
            device.start()
            assert sent[-1] == (2, 1)
            device.data[DreameVacuumProperty.STATE.value] = int(
                DreameVacuumState.SWEEPING
            )
            with pytest.raises(InvalidActionException):
                device.pause()
            assert sent[-1] == (2, 1)
            device.data[DreameVacuumProperty.STATE.value] = int(DreameVacuumState.IDLE)
            device.start()
            assert sent[-1] == (2, 1)
            device.stop()
            assert sent[-1] == (2, 2)
            device.return_to_base()
            assert sent[-1] == (3, 1)
            writes: list[tuple[int, int]] = []

            def record_write(
                siid: int,
                piid: int,
                value: object = None,
                retry_count: int = 2,
                writes: list[tuple[int, int]] = writes,
            ) -> list[dict[str, int]]:
                del value, retry_count
                writes.append((siid, piid))
                return [{"code": 0}]

            device._protocol.set_property = record_write
            assert device.set_volume(40) is False
            assert writes == []
            for siid, aiid in sent:
                assert (siid, aiid) in {(2, 1), (2, 2), (3, 1)}
        finally:
            release_device(device)
