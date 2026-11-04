"""Home Assistant entities for mijia.vacuum.b108zb, the Mijia Sweep Mop 3S."""

from __future__ import annotations

from custom_components.dreame_vacuum.xiaomi import MODEL_MIJIA_SWEEP_MOP_3S
import pytest
from tests.xiaomi.entity_contract import (
    EntityCase,
    assert_entities_read_or_write,
    exercise_home_assistant_entities,
    mijia_b108_entity_case,
)

from homeassistant.core import HomeAssistant

_CASE: EntityCase = mijia_b108_entity_case(
    MODEL_MIJIA_SWEEP_MOP_3S, "Mijia Sweep Mop 3S Sim"
)

pytestmark = [
    pytest.mark.ha,
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


async def test_home_assistant_entities_follow_the_released_spec(
    hass: HomeAssistant,
    socket_enabled: None,
    enable_custom_integrations: None,
    integration_package: object,
) -> None:
    """Create every entity and drive every value the released spec allows."""
    del socket_enabled, enable_custom_integrations, integration_package
    await exercise_home_assistant_entities(hass, _CASE)


async def test_every_entity_reads_or_writes_a_mapped_wire(
    hass: HomeAssistant,
    socket_enabled: None,
    enable_custom_integrations: None,
    integration_package: object,
) -> None:
    """A created entity polls a mapped property or sends a mapped action or write."""
    del socket_enabled, enable_custom_integrations, integration_package
    await assert_entities_read_or_write(hass, _CASE)
