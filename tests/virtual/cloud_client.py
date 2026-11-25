"""Cloud property client that reads a spec robot instead of Xiaomi's cloud."""

from __future__ import annotations

from tests.virtual.spec_robot import SpecRobot


class CloudPropertyClient:
    """Stand-in for the Mi Home device client used after a local token failure."""

    def __init__(self, robot: SpecRobot) -> None:
        self.robot = robot
        self.logged_in = True
        self.connected = True
        self.device_id = "lab-did"
        self.calls: list[str] = []

    def login(self) -> bool:
        """Mark the lab session as signed in. No network."""
        self.logged_in = True
        self.connected = True
        return True

    def send(
        self,
        method: str,
        parameters: object = None,
        retry_count: int = 2,
        timeout: object = None,
    ) -> object | None:
        """Answer one cloud property call from the spec robot."""
        del retry_count, timeout
        self.calls.append(method)
        return self.robot.dispatch(method, parameters)

    def send_async(
        self,
        callback: object,
        method: str,
        parameters: object = None,
        retry_count: int = 2,
    ) -> None:
        """Deliver the same result the sync call would return."""
        result = self.send(method, parameters=parameters, retry_count=retry_count)
        if callable(callback):
            callback(result)
