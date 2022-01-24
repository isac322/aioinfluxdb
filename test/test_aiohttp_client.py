from __future__ import annotations

import random

import pytest

from aioinfluxdb import AioHTTPClient, constants


@pytest.mark.asyncio
class TestAioHTTPClient:
    async def test_ping(self, influxdb_config) -> None:
        client = AioHTTPClient(
            host=influxdb_config.host,
            token=influxdb_config.admin_token,
            port=influxdb_config.port,
        )
        assert await client.ping() is True

    async def test_list_organizations(self, influxdb_config) -> None:
        client = AioHTTPClient(
            host=influxdb_config.host,
            token=influxdb_config.admin_token,
            port=influxdb_config.port,
        )
        orgs = tuple(await client.list_organizations())
        assert len(orgs) == 1
        assert orgs[0].name == influxdb_config.org

    async def test_list_buckets(self, influxdb_config) -> None:
        client = AioHTTPClient(
            host=influxdb_config.host,
            token=influxdb_config.admin_token,
            port=influxdb_config.port,
        )
        buckets = tuple(filter(lambda b: b.type is constants.BucketType.User, await client.list_buckets()))
        assert len(buckets) == 1
        assert buckets[0].name == influxdb_config.bucket

    async def test_create_organization(self, influxdb_config) -> None:
        client = AioHTTPClient(
            host=influxdb_config.host,
            token=influxdb_config.admin_token,
            port=influxdb_config.port,
        )
        org_name = f'org-{random.random() * 100}'
        org = await client.create_organization(name=org_name)
        assert org.name == org_name

    async def test_delete_organization(self, influxdb_config) -> None:
        client = AioHTTPClient(
            host=influxdb_config.host,
            token=influxdb_config.admin_token,
            port=influxdb_config.port,
        )
        org_name = f'org-{random.random() * 100}'
        org = await client.create_organization(name=org_name)
        await client.delete_organization(organization_id=org.id)

    async def test_create_bucket(self, influxdb_config) -> None:
        client = AioHTTPClient(
            host=influxdb_config.host,
            token=influxdb_config.admin_token,
            port=influxdb_config.port,
        )
        org_id = next(iter(await client.list_organizations(organization_name=influxdb_config.org))).id
        bucket = await client.create_bucket(name='test_bucket', organization_id=org_id)
        assert bucket.name == 'test_bucket'
        await client.delete_bucket(bucket_id=bucket.id)

    async def test_write(self, influxdb_config) -> None:
        client = AioHTTPClient(
            host=influxdb_config.host,
            token=influxdb_config.admin_token,
            port=influxdb_config.port,
        )
        await client.write(
            bucket=influxdb_config.bucket,
            organization=influxdb_config.org,
            record=('test', (('a', 1),)),
        )

    async def test_write_multiple(self, influxdb_config) -> None:
        client = AioHTTPClient(
            host=influxdb_config.host,
            token=influxdb_config.admin_token,
            port=influxdb_config.port,
        )
        await client.write_multiple(
            bucket=influxdb_config.bucket,
            organization=influxdb_config.org,
            records=(('test', (('a', 1),)), ('test', (('b', 2),))),
        )
