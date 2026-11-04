"""Every inherited Dreame catalog model keeps upstream detection and behavior."""

from __future__ import annotations

import pytest
from tests.regression.helpers import original_model_ids

_MODEL_IDS = original_model_ids()


@pytest.mark.parametrize("model_id", _MODEL_IDS)
def test_inherited_model_matches_upstream_behavior(
    model_id: str, regression_snapshots: object
) -> None:
    """Catalog row, flags, entities, and fault names stay on the Dreame path."""
    fork = regression_snapshots.fork_model(model_id)
    upstream = regression_snapshots.upstream_model(model_id)
    assert fork["entry"] == upstream["entry"]
    assert fork["catalog_model_id"] == model_id
    assert fork["family"]["applied"] is False
    assert fork["family"]["mapping_replaced"] is False
    assert fork["fault_override"] is None
    assert fork["xiaomi_controls"] == 0
    assert upstream["xiaomi_controls"] == 0
    assert fork["empty"] == upstream["empty"]
    assert fork["reported"] == upstream["reported"]
    assert fork["entities_empty"] == upstream["entities_empty"]
    assert fork["entities_reported"] == upstream["entities_reported"]
    assert fork["entities_empty_cloud"] == upstream["entities_empty_cloud"]
    assert fork["entities_reported_cloud"] == upstream["entities_reported_cloud"]


def test_catalog_keeps_every_inherited_model(regression_snapshots: object) -> None:
    """New models may be added. Inherited model ids are not removed or renamed."""
    fork_ids = set(regression_snapshots.fork["models"])
    upstream_ids = set(regression_snapshots.upstream["models"])
    assert upstream_ids <= fork_ids
    assert len(upstream_ids) == len(_MODEL_IDS)
