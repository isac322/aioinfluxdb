from __future__ import annotations

import asyncio
from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import Any, AsyncIterable, Dict, Iterable, Mapping, Optional, Union, overload

from typing_extensions import final

from aioinfluxdb import constants, types
from aioinfluxdb.flux_table import FluxRecord


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
        precision: constants.WritePrecision = constants.WritePrecision.NanoSecond,
        record: Union[str, types.Record, types.MinimalRecordTuple, types.RecordTuple],
        **kwargs: str,
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
        precision: constants.WritePrecision = constants.WritePrecision.NanoSecond,
        records: Union[
            Iterable[str],
            Iterable[types.Record],
            Iterable[types.MinimalRecordTuple],
            Iterable[types.RecordTuple],
        ],
        **kwargs: str,
    ) -> None:
        raise NotImplementedError

    @overload
    async def flux_query(
        self,
        *,
        organization: str,
        flux_body: str,
        now: Optional[datetime] = None,
        params: Optional[Mapping[str, Any]] = None,
    ) -> AsyncIterable[FluxRecord]:
        pass

    @overload
    async def flux_query(
        self,
        *,
        organization_id: str,
        flux_body: str,
        now: Optional[datetime] = None,
        params: Optional[Mapping[str, Any]] = None,
    ) -> AsyncIterable[FluxRecord]:
        pass

    @abstractmethod
    async def flux_query(
        self,
        *,
        flux_body: str,
        now: Optional[datetime] = None,
        params: Optional[Mapping[str, Any]] = None,
        **kwargs: str,
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

    @classmethod
    def _build_org_query_param(cls, org_map: Mapping[str, str]) -> Dict[str, str]:
        if 'organization_id' in org_map:
            query_params = dict(orgID=org_map['organization_id'])
        else:
            query_params = dict(org=org_map['organization'])
        return query_params
