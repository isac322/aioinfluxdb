from __future__ import annotations

import asyncio
from abc import ABCMeta, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, AsyncIterable, Iterable, Mapping, Optional, Union, overload

from typing_extensions import final

from aioinfluxdb import constants, types
from aioinfluxdb.flux_table import FluxRecord


class _Sentinel(Enum):
    MISSING = object()


class Client(metaclass=ABCMeta):
    _token: str
    _gzip: bool
    _closed: bool

    def __init__(self, token: str, gzip: bool = True) -> None:
        self._token = token
        self._gzip = gzip
        self._closed = False

    def __del__(self) -> None:
        if not self._closed:
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
    async def create_organization(
        self,
        *,
        description: Optional[str] = None,
        name: str,
    ) -> types.Organization:
        pass

    @abstractmethod
    async def get_organization(self, *, organization_id: str) -> Optional[types.Organization]:
        pass

    @abstractmethod
    async def delete_organization(self, *, organization_id: str) -> None:
        pass

    @abstractmethod
    async def create_bucket(
        self,
        *,
        description: Optional[str] = None,
        name: str,
        organization_id: str,
        retention_rules: Iterable[types.RetentionRule] = (),
        rp: Optional[str] = None,
        schema_type: Optional[str] = None,
    ) -> types.Bucket:
        pass

    @abstractmethod
    async def delete_bucket(self, *, bucket_id: str) -> None:
        pass

    @abstractmethod
    async def get_bucket(self, *, bucket_id: str) -> Optional[types.Bucket]:
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

    @overload
    async def flux_query(self, *, organization: str, flux_body: str) -> AsyncIterable[FluxRecord]:
        pass

    @overload
    async def flux_query(self, *, organization_id: str, flux_body: str) -> AsyncIterable[FluxRecord]:
        pass

    @abstractmethod
    async def flux_query(
        self,
        *,
        organization: Union[str, _Sentinel] = _Sentinel.MISSING,
        organization_id: Union[str, _Sentinel] = _Sentinel.MISSING,
        flux_body: str,
        now: Optional[datetime] = None,
        params: Optional[Mapping[str, Any]] = None,
    ) -> AsyncIterable[FluxRecord]:
        raise NotImplementedError

    @final
    async def close(self) -> None:
        await self._close()
        self._closed = True

    @abstractmethod
    async def _close(self) -> None:
        raise NotImplementedError

    @property
    def api_token(self) -> str:
        return self._token
