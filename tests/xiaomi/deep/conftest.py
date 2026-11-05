"""Parametrize each model module from its fetched spec."""

from __future__ import annotations

from tests.xiaomi.deep.cases import (
    action_cases,
    address_cases,
    control_cases,
    fault_cases,
    property_cases,
    value_cases,
)


def pytest_generate_tests(metafunc: object) -> None:
    """Attach spec cases to tests that declare them."""
    module = getattr(metafunc, "module", None)
    model = getattr(module, "MODEL", None)
    names = getattr(metafunc, "fixturenames", ())
    if not isinstance(model, str):
        return
    parametrize = getattr(metafunc, "parametrize", None)
    if not callable(parametrize):
        return
    specs = {
        "spec_property": property_cases(model),
        "spec_action": action_cases(model),
        "spec_value": value_cases(model),
        "spec_fault": fault_cases(model),
        "spec_control": control_cases(model),
        "spec_address": address_cases(model),
    }
    for name, cases in specs.items():
        if name not in names or not cases:
            continue
        parametrize(name, cases, ids=[case.case_id for case in cases])
