from __future__ import annotations

import http
from typing import Iterable, Mapping, Optional, Union, overload

import aiohttp
import orjson
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
        params = {
            k: v
            for k, v in dict(
                descending=int(descending),
                limit=limit,
                offset=offset,
                org=organization_name,
                orgID=organization_id,
                userID=user_id,
            ).items()
            if v is not None
        }
        headers = {aiohttp.hdrs.AUTHORIZATION: f'Token {self.api_token}'}

        if self._gzip:
            headers[aiohttp.hdrs.ACCEPT_ENCODING] = 'gzip'

        res = await self._session.get(
            '/api/v2/orgs',
            params=params,
            headers=headers,
        )
        # TODO: error handling
        res.raise_for_status()
        # TODO: Utilize `links`
        buckets = await res.json(loads=orjson.loads)
        return map(types.Organization.from_json, buckets['orgs'])

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
        params = {
            k: v
            for k, v in dict(
                after=after,
                id=bucket_id,
                limit=limit,
                name=name,
                offset=offset,
                org=organization,
                orgID=organization_id,
            ).items()
            if v is not None
        }
        headers = {aiohttp.hdrs.AUTHORIZATION: f'Token {self.api_token}'}

        if self._gzip:
            headers[aiohttp.hdrs.ACCEPT_ENCODING] = 'gzip'

        res = await self._session.get(
            '/api/v2/buckets',
            params=params,
            headers=headers,
        )
        # TODO: error handling
        res.raise_for_status()
        # TODO: Utilize `links`
        buckets = await res.json(loads=orjson.loads)
        return map(types.Bucket.from_json, buckets['buckets'])

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
        data = dict(
            name=name,
            orgID=organization_id,
        )
        retention_rules = tuple(retention_rules)
        if len(retention_rules) != 0:
            data['retentionRules'] = tuple(map(types.RetentionRule.to_json, retention_rules))
        if description is not None:
            data['description'] = description
        if rp is not None:
            data['rp'] = rp
        if schema_type is not None:
            data['schemaType'] = schema_type
        ser_data = orjson.dumps(data)

        headers = {aiohttp.hdrs.AUTHORIZATION: f'Token {self.api_token}'}
        if self._gzip:
            # bucket creation does not support gzip body
            headers[aiohttp.hdrs.ACCEPT_ENCODING] = 'gzip'

        res = await self._session.post(
            '/api/v2/buckets',
            data=ser_data,
            headers=headers,
        )
        res.raise_for_status()
        return types.Bucket.from_json(await res.json(loads=orjson.loads))

    async def delete_bucket(self, *, bucket_id: str) -> None:
        headers = {aiohttp.hdrs.AUTHORIZATION: f'Token {self.api_token}'}

        res = await self._session.delete(
            f'/api/v2/buckets/{bucket_id}',
            headers=headers,
        )
        res.raise_for_status()

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
