from __future__ import annotations

import aiohttp.web
import pytest

from aioinfluxdb import AioHTTPClient, constants, types
from aioinfluxdb.aiohttp_client import _WithAsyncReadAdapter


@pytest.mark.asyncio
class TestAioHTTPClient:
    async def test_ping(self, aiohttp_influx: AioHTTPClient) -> None:
        assert await aiohttp_influx.ping() is True

    async def test_list_organizations(self, aiohttp_influx: AioHTTPClient, organization: types.Organization) -> None:
        orgs = tuple(await aiohttp_influx.list_organizations(organization_name=organization.name))
        assert len(orgs) == 1
        assert orgs[0].name == organization.name

    async def test_list_buckets(self, aiohttp_influx: AioHTTPClient, bucket: types.Bucket) -> None:
        buckets = tuple(
            filter(
                lambda b: b.type is constants.BucketType.User,
                await aiohttp_influx.list_buckets(organization_id=bucket.organization_id),
            )
        )
        assert len(buckets) == 1
        assert buckets[0].id == bucket.id
        assert buckets[0].name == bucket.name

    async def test_create_organization(self, aiohttp_influx: AioHTTPClient, organization_name: str) -> None:
        org = await aiohttp_influx.create_organization(name=organization_name)
        assert org.name == organization_name
        try:
            await aiohttp_influx.delete_organization(organization_id=org.id)
        except Exception:
            pass

    async def test_delete_organization(self, aiohttp_influx: AioHTTPClient, organization: types.Organization) -> None:
        await aiohttp_influx.delete_organization(organization_id=organization.id)

    async def test_get_organization(self, aiohttp_influx: AioHTTPClient, organization: types.Organization) -> None:
        org = await aiohttp_influx.get_organization(organization_id=organization.id)
        assert org.id == organization.id
        assert org.name == organization.name

    async def test_create_bucket(
        self,
        aiohttp_influx: AioHTTPClient,
        organization: types.Organization,
        bucket_name: str,
    ) -> None:
        bucket = await aiohttp_influx.create_bucket(name=bucket_name, organization_id=organization.id)
        assert bucket.name == bucket_name
        try:
            await aiohttp_influx.delete_bucket(bucket_id=bucket.id)
        except Exception:
            pass

    async def test_delete_bucket(self, aiohttp_influx: AioHTTPClient, bucket: types.Bucket) -> None:
        await aiohttp_influx.delete_bucket(bucket_id=bucket.id)

    async def test_get_bucket(self, aiohttp_influx: AioHTTPClient, bucket: types.Bucket) -> None:
        b = await aiohttp_influx.get_bucket(bucket_id=bucket.id)
        assert b.id == bucket.id
        assert b.name == bucket.name

    async def test_write(self, aiohttp_influx: AioHTTPClient, bucket: types.Bucket) -> None:
        await aiohttp_influx.write(
            bucket=bucket.id,
            organization_id=bucket.organization_id,
            record=('test', (('a', 1),)),
        )

    async def test_write_multiple(self, aiohttp_influx: AioHTTPClient, bucket: types.Bucket) -> None:
        await aiohttp_influx.write_multiple(
            bucket=bucket.id,
            organization_id=bucket.organization_id,
            records=(('test', (('a', 1),)), ('test', (('b', 2),))),
        )

    async def test_flux_query(self, aiohttp_influx: AioHTTPClient, bucket: types.Bucket) -> None:
        await aiohttp_influx.write_multiple(
            bucket=bucket.id,
            organization_id=bucket.organization_id,
            records=(('test', (('a', 1),)), ('test', (('b', 2),)), types.Record('test1', (('a', 1), ('b', 2)))),
        )

        r = await aiohttp_influx.flux_query(
            organization_id=bucket.organization_id,
            flux_body=f'''
            from(bucket: "{bucket.name}")
              |> range(start: -1h)
              |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
            ''',
        )
        async for e in r:
            print(e)
        print(r)


@pytest.mark.asyncio
class TestWithAsyncReadAdapter:
    @pytest.mark.parametrize(
        ('body', 'size', 'expected'),
        (
            ('한2글', 2, '한2'),
            ('the 한글', 4, 'the '),
            ('the 한글', 5, 'the 한'),
            ('한2글', 3, '한2글'),
            ('한글', 2, '한글'),
            ('한글', 1, '한'),
            ('ads', 1, 'a'),
        ),
    )
    async def test_read(self, aiohttp_raw_server, aiohttp_client, body, size, expected):
        async def handler(_):
            return aiohttp.web.Response(text=body)

        raw_server = await aiohttp_raw_server(handler)
        client = await aiohttp_client(raw_server)
        res = await client.get('/')
        adapter = _WithAsyncReadAdapter(res)

        assert await adapter.read(size) == expected
