from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable, Mapping, NamedTuple, Optional, Tuple, Union

from dateutil.parser import isoparse
from typing_extensions import TypeAlias, TypedDict

from aioinfluxdb import constants

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


class _RetentionRule(TypedDict, total=False):
    everySeconds: int
    shardGroupDurationSeconds: int
    type: str


@dataclass(frozen=True)
class RetentionRule:
    every_seconds: int
    shard_group_duration_seconds: Optional[int]
    type: str

    @classmethod
    def from_json(cls, data: _RetentionRule) -> RetentionRule:
        return cls(
            every_seconds=data['everySeconds'],
            shard_group_duration_seconds=data.get('shardGroupDurationSeconds'),
            type=data['type'],
        )

    def to_json(self) -> _RetentionRule:
        ret = _RetentionRule(
            everySeconds=self.every_seconds,
            type=self.type,
        )
        if self.shard_group_duration_seconds is not None:
            ret['shardGroupDurationSeconds'] = self.shard_group_duration_seconds
        return ret


class _Label(TypedDict):
    id: str
    name: str
    orgID: str
    properties: Mapping[str, Any]


@dataclass(frozen=True)
class Label:
    id: str
    name: str
    organization_id: str
    properties: Mapping[str, Any]

    @classmethod
    def from_json(cls, data: _Label) -> Label:
        return cls(
            id=data['id'],
            name=data['name'],
            organization_id=data['orgID'],
            properties=data['properties'],
        )


class _Bucket(TypedDict, total=False):
    createdAt: str
    description: str
    id: str
    labels: Iterable[_Label]
    name: str
    orgID: str
    retentionRules: Iterable[_RetentionRule]
    rp: str
    schemaType: str
    type: str
    updatedAt: str


@dataclass(frozen=True)
class Bucket:
    created_at: Optional[datetime]
    description: Optional[str]
    id: Optional[str]
    labels: Tuple[Label, ...]
    name: str
    organization_id: Optional[str]
    retention_rules: Tuple[RetentionRule, ...]
    rp: Optional[str]
    schema_type: Optional[str]
    type: str
    updated_at: Optional[datetime]

    @classmethod
    def from_json(cls, data: _Bucket) -> Bucket:
        return cls(
            created_at=isoparse(data['createdAt']) if 'createdAt' in data else None,
            description=data.get('description'),
            id=data.get('id'),
            labels=tuple(map(Label.from_json, data.get('labels', ()))),
            name=data['name'],
            organization_id=data.get('orgID'),
            retention_rules=tuple(map(RetentionRule.from_json, data['retentionRules'])),
            rp=data.get('rp'),
            schema_type=constants.BucketSchemaType(data['schemaType']) if 'schemaType' in data else None,
            type=constants.BucketType(data.get('type', constants.BucketType.User)),
            updated_at=isoparse(data['updatedAt']) if 'updatedAt' in data else None,
        )


class _Organization(TypedDict, total=False):
    createdAt: str
    description: str
    id: str
    name: str
    status: str
    updatedAt: str


@dataclass(frozen=True)
class Organization:
    created_at: Optional[datetime]
    description: Optional[str]
    id: Optional[str]
    name: str
    status: constants.OrganizationStatus
    updated_at: Optional[datetime]

    @classmethod
    def from_json(cls, data: _Organization) -> Organization:
        return cls(
            created_at=isoparse(data['createdAt']) if 'createdAt' in data else None,
            description=data.get('description'),
            id=data.get('id'),
            name=data['name'],
            status=constants.OrganizationStatus(data.get('status', constants.OrganizationStatus.Active)),
            updated_at=isoparse(data['updatedAt']) if 'updatedAt' in data else None,
        )
