"""A property poll must survive a reply that is not a property list."""

from __future__ import annotations

from types import SimpleNamespace

from custom_components.xiaomi_robot_vacuum.dreame.device import DreameVacuumDevice
from custom_components.xiaomi_robot_vacuum.dreame.exceptions import DeviceException
from custom_components.xiaomi_robot_vacuum.dreame.map import DreameVacuumMapDecoder
from custom_components.xiaomi_robot_vacuum.dreame.types import DreameVacuumProperty
from hypothesis import given, settings, strategies as st
import pytest

_STATE = DreameVacuumProperty.STATE


def _device(reply: object) -> DreameVacuumDevice:
    device = object.__new__(DreameVacuumDevice)
    device._default_properties = [_STATE]
    device.property_mapping = {_STATE: {"siid": 2, "piid": 1}}
    device._ready = True
    device.data = {_STATE.value: 2}
    device.info = SimpleNamespace(model="xiaomi.vacuum.d109gl")
    device._configured_model = "xiaomi.vacuum.d109gl"
    device.capability = SimpleNamespace(loaded=True, mijia=True)
    device._property_codec = None
    device._dirty_data = {}
    device._property_update_callback = {}
    device._protocol = SimpleNamespace(
        dreame_cloud=False,
        prefer_cloud=False,
        get_properties=lambda _batch, timeout=None: reply,
    )
    return device


def test_a_dict_reply_is_unavailable() -> None:
    """An error object is not a property list."""
    device = _device({"code": -9999, "message": "rejected"})
    with pytest.raises(DeviceException):
        device._request_properties()
    assert device.data[_STATE.value] == 2


def test_a_string_reply_is_unavailable() -> None:
    """A timeout body must not be walked as property items."""
    device = _device("timeout")
    with pytest.raises(DeviceException):
        device._request_properties()
    assert device.data[_STATE.value] == 2


def test_a_broken_item_is_skipped() -> None:
    """One bad item does not discard the value already stored."""
    device = _device(
        [
            {"code": 0, "value": 9},
            {"did": "2.1", "code": 0, "value": 4},
            {"did": "0", "value": 7},
        ]
    )
    assert device._request_properties() is False
    assert device.data[_STATE.value] == 2


def test_an_unexpected_error_code_leaves_the_stored_value() -> None:
    """A negative code is a refusal, not a new state."""
    device = _device([{"did": "0", "siid": 2, "piid": 1, "code": -4004}])
    assert device._request_properties() is False
    assert device.data[_STATE.value] == 2


def test_bad_map_text_does_not_raise() -> None:
    """A published frame that is not base64 returns no map."""
    assert DreameVacuumMapDecoder.decode_map("%%%") is None
    assert DreameVacuumMapDecoder.decode_map("abc") is None


@settings(max_examples=30, deadline=None, derandomize=True)
@given(
    reply=st.one_of(
        st.none(),
        st.integers(),
        st.text(max_size=20),
        st.dictionaries(st.text(max_size=8), st.integers(), max_size=3),
        st.lists(
            st.one_of(
                st.none(),
                st.text(max_size=8),
                st.fixed_dictionaries(
                    {},
                    optional={
                        "did": st.one_of(st.integers(), st.text(max_size=6)),
                        "code": st.integers(min_value=-20, max_value=2),
                        "value": st.one_of(
                            st.integers(), st.text(max_size=4), st.none()
                        ),
                        "siid": st.integers(min_value=0, max_value=5),
                        "piid": st.integers(min_value=0, max_value=5),
                    },
                ),
            ),
            max_size=4,
        ),
    )
)
def test_a_random_reply_raises_only_device_unavailable(reply: object) -> None:
    """Malformed traffic fails the poll or leaves the previous value."""
    device = _device(reply)
    try:
        changed = device._request_properties()
    except DeviceException:
        assert device.data[_STATE.value] == 2
        return
    assert changed in (True, False)
    assert isinstance(device.data[_STATE.value], int)
