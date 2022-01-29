"""
Based on https://github.com/influxdata/influxdb-client-python 1.25.0
"""

from __future__ import annotations

from typing import Any


class FluxQueryException(Exception):
    """The exception from InfluxDB."""

    message: str
    reference: Any

    def __init__(self, message: str, reference: Any) -> None:
        """Initialize defaults."""
        self.message = message
        self.reference = reference


class FluxCsvParserException(Exception):
    """The exception for not parsable data."""

    pass
