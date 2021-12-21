from __future__ import annotations

import re
from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import Iterable, Optional, Pattern, SupportsFloat, SupportsInt, Union
from typing_extensions import Final

from aioinfluxdb import types


class RecordSerializer(metaclass=ABCMeta):
    @abstractmethod
    def serialize_record(self, record: Union[types.Record, types.MinimalRecordTuple, types.RecordTuple]) -> str:
        raise NotImplementedError


class DefaultRecordSerializer(RecordSerializer):
    _comma_space: Final[Pattern[str]] = re.compile(r'[, ]')
    _comma_equal_space: Final[Pattern[str]] = re.compile(r'[, =]')
    _quote_backslash: Final[Pattern[str]] = re.compile(r'["\\]')

    @classmethod
    def serialize_record(cls, record: Union[types.Record, types.MinimalRecordTuple, types.RecordTuple]) -> str:
        measurement: str
        tag_set: Optional[str] = None
        field_set: str
        timestamp: Optional[str] = None

        if isinstance(record, types.Record):
            measurement = cls._serialize_measurement(record.measurement)
            tag_set = cls._serialize_tag_set(record.tag_set)
            field_set = cls._serialize_field_set(record.field_set)
            timestamp = cls._serialize_timestamp(record.timestamp)
        elif (
            isinstance(record, tuple)
            and len(record) == 2
            and isinstance(record[0], str)
            and isinstance(record[1], Iterable)
        ):
            measurement = cls._serialize_measurement(record[0])
            field_set = cls._serialize_field_set(record[1])
        elif (
            isinstance(record, tuple)
            and len(record) == 4
            and isinstance(record[0], str)
            and (isinstance(record[1], Iterable) or record[1] is None)
            and isinstance(record[2], Iterable)
            and (isinstance(record[3], (datetime, int, float)) or record[3] is None)
        ):
            measurement = cls._serialize_measurement(record[0])
            tag_set = cls._serialize_tag_set(record[1])
            field_set = cls._serialize_field_set(record[2])
            timestamp = cls._serialize_timestamp(record[3])
        else:
            raise ValueError(f'Unsupported record: {record.__class__}')

        ret = measurement
        if tag_set is not None:
            ret += f',{tag_set}'
        ret += f' {field_set}'
        if timestamp is not None:
            ret += f' {timestamp}'
        return ret

    @classmethod
    def _serialize_measurement(cls, name: str) -> str:
        return cls._comma_space.sub(r'\\\g<0>', name)

    @classmethod
    def _serialize_tag_set(cls, tag_set: Optional[types.TagSetType]) -> Optional[str]:
        if tag_set is None:
            return None

        ret = ','.join('='.join(map(cls._serialize_member, pair)) for pair in tag_set)
        if len(ret) == 0:
            return None
        return ret

    @classmethod
    def _serialize_field_set(cls, field_set: types.FieldSetType) -> str:
        return ','.join(f'{cls._serialize_member(pair[0])}={cls._serialize_field_value(pair[1])}' for pair in field_set)

    @classmethod
    def _serialize_timestamp(cls, timestamp: Optional[types.TimestampType]) -> Optional[str]:
        if timestamp is None:
            return None

        if isinstance(timestamp, datetime):
            return str(int(timestamp.timestamp() * 1_000_000))
        elif isinstance(timestamp, float):
            return str(int(timestamp * 1_000_000))
        elif isinstance(timestamp, int):
            return str(timestamp)
        else:
            raise ValueError(f'Unsupported timestamp type: {timestamp.__class__}')

    @classmethod
    def _serialize_field_value(cls, value: types.FieldType) -> str:
        if isinstance(value, float):
            return cls._serialize_float_field_value(value)
        elif isinstance(value, bool):
            return cls._serialize_bool_field_value(value)
        elif isinstance(value, int):
            return cls._serialize_int_field_value(value)
        elif isinstance(value, str):
            return cls._serialize_string_field_value(value)
        elif isinstance(value, SupportsFloat):
            return cls._serialize_float_field_value(float(value))
        elif isinstance(value, SupportsInt):
            return cls._serialize_int_field_value(int(value))
        else:
            return cls._serialize_string_field_value(str(value))

    @classmethod
    def _serialize_member(cls, member: str) -> str:
        return cls._comma_equal_space.sub(r'\\\g<0>', member)

    @classmethod
    def _serialize_string_field_value(cls, value: str) -> str:
        value = cls._quote_backslash.sub(r'\\\g<0>', value)
        if ' ' in value:
            return f'"{value}"'
        return value

    @classmethod
    def _serialize_int_field_value(cls, value: int) -> str:
        if value.bit_length() > 64:
            return str(float(value))
        elif value.bit_length() == 64:
            if value < 0:
                if value < -9223372036854775808:
                    return str(float(value))
                else:
                    return f'{value}i'
            else:
                return f'{value}u'
        else:
            return f'{value}i'

    @classmethod
    def _serialize_float_field_value(cls, value: float) -> str:
        return str(value)

    @classmethod
    def _serialize_bool_field_value(cls, value: bool) -> str:
        return 't' if value else 'f'
