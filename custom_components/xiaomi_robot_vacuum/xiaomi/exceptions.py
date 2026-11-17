"""Exceptions raised by the Xiaomi vacuum family."""

from __future__ import annotations


class XiaomiTransportException(Exception):  # noqa: N818 - core uses Exception
    """The local miIO property transport could not be built."""


class XiaomiControlException(Exception):  # noqa: N818 - core uses Exception
    """A Xiaomi control read or write was rejected."""

    def __init__(self, key: str) -> None:
        self.key = key
        super().__init__(key)


class XiaomiValueException(XiaomiControlException):
    """An outgoing value is outside the published spec for this model."""
