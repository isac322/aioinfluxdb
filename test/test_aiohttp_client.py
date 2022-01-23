from __future__ import annotations

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

    async def test_list_buckets(self, influxdb_config) -> None:
        client = AioHTTPClient(
            host=influxdb_config.host,
            token=influxdb_config.admin_token,
            port=influxdb_config.port,
        )
        buckets = tuple(filter(lambda b: b.type is constants.BucketType.User, await client.list_buckets()))
        assert len(buckets) == 1
        assert buckets[0].name == influxdb_config.bucket

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
