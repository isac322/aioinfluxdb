from __future__ import annotations

from enum import Enum


class WritePrecision(str, Enum):
    MilliSecond = 'ms'
    Second = 's'
    MicroSecond = 'us'
    NanoSecond = 'ns'
