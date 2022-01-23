from __future__ import annotations

from enum import Enum


class WritePrecision(str, Enum):
    MilliSecond = 'ms'
    Second = 's'
    MicroSecond = 'us'
    NanoSecond = 'ns'


class RetentionRuleType(str, Enum):
    Expire = 'expire'


class BucketSchemaType(str, Enum):
    Implicit = 'implicit'
    Explicit = 'explicit'


class BucketType(str, Enum):
    User = 'user'
    System = 'system'
