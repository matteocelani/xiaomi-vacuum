"""Session fixture for the inherited Dreame golden snapshots."""

from __future__ import annotations

import pytest
from tests.regression.helpers import RegressionSnapshots, load_snapshots


@pytest.fixture(scope="session")
def regression_snapshots() -> RegressionSnapshots:
    """Snapshot this tree and the inherited upstream tree once per session."""
    return load_snapshots()
