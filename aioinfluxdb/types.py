from __future__ import annotations

from datetime import datetime
from typing import Iterable, NamedTuple, Optional, Tuple, Union

from typing_extensions import TypeAlias

TagType: TypeAlias = Tuple[str, str]
TagSetType: TypeAlias = Iterable[Tuple[str, str]]
FieldType: TypeAlias = Union[int, float, bool, str]
FieldSetType: TypeAlias = Iterable[Tuple[str, FieldType]]
TimestampType: TypeAlias = Union[datetime, int, float]

MinimalRecordTuple: TypeAlias = Tuple[str, FieldSetType]
""" measurement, field-set """

RecordTuple: TypeAlias = Tuple[str, Optional[TagSetType], FieldSetType, Optional[TimestampType]]
""" measurement, field_set, field-set, timestamp """


class Record(NamedTuple):
    measurement: str
    field_set: FieldSetType
    tag_set: Optional[TagSetType] = None
    timestamp: Optional[TimestampType] = None

    def __repr__(self) -> str:
        body = ', '.join((f'{key}={getattr(self, key)}' for key in self._fields if getattr(self, key) is not None))
        return f'<{self.__class__.__name__} {body}>'
