from __future__ import annotations

import http
from typing import Iterable, Mapping, Optional, Union, overload

import aiohttp
from isal import igzip as gzip

from aioinfluxdb import constants, serializer, types
from aioinfluxdb.client import Client, _Sentinel


class AioHTTPClient(Client):
    _host: str
    _port: int
    _session: aiohttp.ClientSession

    def __init__(
        self,
        host: str,
        token: str,
        port: int = 8086,
        tls: bool = False,
        connector: Optional[aiohttp.BaseConnector] = None,
        session: Optional[aiohttp.ClientSession] = None,
        gzip: bool = True,
    ) -> None:
        super().__init__(token=token, gzip=gzip)

        self._host = host
        self._port = port

        if connector is not None and session is not None:
            raise ValueError('`connector` and `session` cannot be set at the same time')
        elif session is not None:
            self._session = session
        else:
            self._session = aiohttp.ClientSession(f'{"https" if tls else "http"}://{host}:{port}', connector=connector)

    async def ping(self) -> bool:
        res = await self._session.get('/ping')
        return res.status in (http.HTTPStatus.OK, http.HTTPStatus.NO_CONTENT)

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

    async def write(
        self,
        *,
        bucket: str,
        organization: Union[str, _Sentinel] = _Sentinel.MISSING,
        organization_id: Union[str, _Sentinel] = _Sentinel.MISSING,
        precision: constants.WritePrecision = constants.WritePrecision.NanoSecond,
        record: Union[str, types.Record, types.MinimalRecordTuple, types.RecordTuple],
    ) -> None:
        data = serializer.DefaultRecordSerializer.serialize_record(record)
        headers = {aiohttp.hdrs.AUTHORIZATION: f'Token {self.api_token}'}

        if self._gzip:
            data = gzip.compress(data.encode())
            headers[aiohttp.hdrs.CONTENT_ENCODING] = 'gzip'
            headers[aiohttp.hdrs.ACCEPT_ENCODING] = 'gzip'

        res = await self._session.post(
            '/api/v2/write',
            params=self._build_query_params(
                bucket=bucket,
                organization=organization,
                organization_id=organization_id,
                precision=precision.value,
            ),
            headers=headers,
            data=data,
        )
        res.raise_for_status()

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
        data = '\n'.join(map(serializer.DefaultRecordSerializer.serialize_record, records))
        headers = {aiohttp.hdrs.AUTHORIZATION: f'Token {self.api_token}'}

        if self._gzip:
            data = gzip.compress(data.encode())
            headers[aiohttp.hdrs.CONTENT_ENCODING] = 'gzip'
            headers[aiohttp.hdrs.ACCEPT_ENCODING] = 'gzip'

        res = await self._session.post(
            '/api/v2/write',
            params=self._build_query_params(
                bucket=bucket,
                organization=organization,
                organization_id=organization_id,
                precision=precision.value,
            ),
            headers=headers,
            data=data,
        )
        res.raise_for_status()

    @classmethod
    def _build_query_params(
        cls,
        *,
        bucket: str,
        organization: Union[str, _Sentinel],
        organization_id: Union[str, _Sentinel],
        precision: constants.WritePrecision,
    ) -> Mapping[str, str]:
        ret = dict(
            bucket=bucket,
            precision=precision,
        )
        if organization_id is not _Sentinel.MISSING:
            ret['orgID'] = organization_id
        if organization is not _Sentinel.MISSING:
            ret['org'] = organization
        return ret

    async def close(self) -> None:
        await self._session.close()
