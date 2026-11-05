"""Deep spec-derived tests for xiaomi.vacuum.d102ev."""

from __future__ import annotations

from hypothesis import given, settings, strategies as st
import pytest
from tests.xiaomi.deep.checks import (
    check_action,
    check_address,
    check_capability_flags,
    check_catalog,
    check_catalog_version,
    check_cloud_fallback,
    check_configured_family,
    check_control,
    check_control_refresh,
    check_fault,
    check_outgoing_range,
    check_property,
    check_record,
    check_send_async_transport,
    check_set_properties_conversion,
    check_start_custom,
    check_status_wire,
    check_unknown_state_task,
    check_value,
)

MODEL = "xiaomi.vacuum.d102ev"


def test_fetched_spec_matches_the_recorded_document() -> None:
    check_record(MODEL)


def test_catalog_accepts_the_model() -> None:
    check_catalog(MODEL)


def test_mapped_spec_is_the_newest_released_version() -> None:
    check_catalog_version(MODEL)


def test_property_is_mapped_or_omitted(spec_property) -> None:
    check_property(spec_property)


def test_action_is_mapped_or_omitted(spec_action) -> None:
    check_action(spec_action)


def test_mapped_address_exists_in_this_spec(spec_address) -> None:
    check_address(spec_address)


def test_value_list_entry_converts(spec_value) -> None:
    check_value(spec_value)


def test_fault_name_comes_from_the_spec(spec_fault) -> None:
    check_fault(spec_fault)


def test_capability_flags_follow_the_map() -> None:
    check_capability_flags(MODEL)


def test_missing_credentials_keep_the_cloud_path() -> None:
    check_cloud_fallback(MODEL)


@settings(max_examples=20, deadline=None, derandomize=True)
@given(st.integers(min_value=-8, max_value=80))
def test_status_wire_is_mapped_only_when_the_spec_lists_it(wire: int) -> None:
    check_status_wire(MODEL, wire)


@settings(max_examples=12, deadline=None, derandomize=True)
@given(st.integers(min_value=-5, max_value=12))
def test_outgoing_value_outside_the_spec_is_refused(sample: int) -> None:
    check_outgoing_range(MODEL, sample)


def test_unknown_status_does_not_complete_the_task() -> None:
    check_unknown_state_task(MODEL)


def test_configured_model_installs_before_runtime_info() -> None:
    check_configured_family(MODEL)


def test_async_property_calls_use_the_xiaomi_transport() -> None:
    check_send_async_transport()


def test_control_matches_its_spec_item(spec_control) -> None:
    check_control(spec_control)


def test_one_failing_control_does_not_fail_the_refresh() -> None:
    check_control_refresh(MODEL)


@pytest.mark.enable_socket
@pytest.mark.allow_hosts(["127.0.0.1"])
def test_start_custom_uses_a_spec_property() -> None:
    check_start_custom(MODEL)


@pytest.mark.enable_socket
@pytest.mark.allow_hosts(["127.0.0.1"])
def test_batch_write_uses_outgoing_conversion() -> None:
    check_set_properties_conversion(MODEL)
