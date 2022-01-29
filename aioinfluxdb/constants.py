from __future__ import annotations

from enum import Enum, IntEnum


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


class OrganizationStatus(str, Enum):
    Active = 'active'
    Inactive = 'inactive'


class FluxSerializationMode(IntEnum):
    """The type how we wan't to serialize data."""

    tables = 1
    stream = 2
    dataFrame = 3
