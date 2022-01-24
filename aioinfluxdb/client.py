from __future__ import annotations

import asyncio
from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Iterable, Optional, Union, overload

from aioinfluxdb import constants, types


class _Sentinel(Enum):
    MISSING = object()


class Client(metaclass=ABCMeta):
    _token: str
    _gzip: bool

    def __init__(self, token: str, gzip: bool = True) -> None:
        self._token = token
        self._gzip = gzip

    def __del__(self) -> None:
        asyncio.create_task(self.close())

    @abstractmethod
    async def ping(self) -> bool:
        """`true` if pong received"""
        raise NotImplementedError

    @abstractmethod
    async def list_organizations(
        self,
        *,
        descending: bool = False,
        limit: int = 20,
        offset: int = 0,
        organization_name: Optional[str] = None,
        organization_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Iterable[types.Organization]:
        pass

    @abstractmethod
    async def list_buckets(
        self,
        *,
        after: Optional[str] = None,
        bucket_id: Optional[str] = None,
        limit: int = 20,
        name: Optional[str] = None,
        offset: int = 0,
        organization: Optional[str] = None,
        organization_id: Optional[str] = None,
    ) -> Iterable[types.Bucket]:
        pass

    @abstractmethod
    async def create_bucket(
        self,
        *,
        description: Optional[str] = None,
        name: str,
        organization_id: str,
        retention_rules: Iterable[types.RetentionRule, ...] = (),
        rp: Optional[str] = None,
        schema_type: Optional[str] = None,
    ) -> types.Bucket:
        pass

    @abstractmethod
    async def delete_bucket(self, *, bucket_id: str) -> None:
        pass

    @overload
    async def write(
        self,
        *,
        bucket: str,
        organization: str,
        precision: constants.WritePrecision = constants.WritePrecision.NanoSecond,
        record: Union[str, types.Record, types.MinimalRecordTuple, types.RecordTuple],
    ) -> None:
        pass

    @overload
    async def write(
        self,
        *,
        bucket: str,
        organization_id: str,
        precision: constants.WritePrecision = constants.WritePrecision.NanoSecond,
        record: Union[str, types.Record, types.MinimalRecordTuple, types.RecordTuple],
    ) -> None:
        pass

    @abstractmethod
    async def write(
        self,
        *,
        bucket: str,
        organization: Union[str, _Sentinel] = _Sentinel.MISSING,
        organization_id: Union[str, _Sentinel] = _Sentinel.MISSING,
        precision: constants.WritePrecision = constants.WritePrecision.NanoSecond,
        record: Union[str, types.Record, types.MinimalRecordTuple, types.RecordTuple],
    ) -> None:
        raise NotImplementedError

    @overload
    async def write_multiple(
        self,
        *,
        bucket: str,
        organization: str,
        precision: constants.WritePrecision = constants.WritePrecision.NanoSecond,
        records: Union[
            Iterable[str],
            Iterable[types.Record],
            Iterable[types.MinimalRecordTuple],
            Iterable[types.RecordTuple],
        ],
    ) -> None:
        pass

    @overload
    async def write_multiple(
        self,
        *,
        bucket: str,
        organization_id: str,
        precision: constants.WritePrecision = constants.WritePrecision.NanoSecond,
        records: Union[
            Iterable[str],
            Iterable[types.Record],
            Iterable[types.MinimalRecordTuple],
            Iterable[types.RecordTuple],
        ],
    ) -> None:
        pass

    @abstractmethod
    async def write_multiple(
        self,
        *,
        bucket: str,
        organization: Union[str, _Sentinel] = _Sentinel.MISSING,
        organization_id: Union[str, _Sentinel] = _Sentinel.MISSING,
        precision: constants.WritePrecision = constants.WritePrecision.NanoSecond,
        records: Union[
            Iterable[str],
            Iterable[types.Record],
            Iterable[types.MinimalRecordTuple],
            Iterable[types.RecordTuple],
        ],
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError

    @property
    def api_token(self) -> str:
        return self._token
