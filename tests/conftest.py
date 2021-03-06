from __future__ import annotations

import os
import random
from dataclasses import dataclass

import pytest
import pytest_asyncio

from aioinfluxdb import AioHTTPClient, types


@dataclass(frozen=True)
class InfluxDBConfig:
    host: str
    port: int
    admin_token: str


@pytest.fixture(scope='session')
def influxdb_config() -> InfluxDBConfig:
    return InfluxDBConfig(
        host=os.environ['INFLUXDB_HOST'],
        port=os.environ.get('INFLUXDB_PORT', 8086),
        admin_token=os.environ['INFLUXDB_ADMIN_TOKEN'],
    )


@pytest_asyncio.fixture(scope='function')
async def aiohttp_influx(influxdb_config) -> AioHTTPClient:
    client = AioHTTPClient(
        host=influxdb_config.host,
        token=influxdb_config.admin_token,
        port=influxdb_config.port,
    )
    yield client
    await client.close()


@pytest.fixture(scope='function')
def organization_name() -> str:
    return f'org-{random.random() * 100:.3f}'


@pytest_asyncio.fixture(scope='function')
async def organization(aiohttp_influx: AioHTTPClient, organization_name: str) -> types.Organization:
    org = await aiohttp_influx.create_organization(name=organization_name)
    try:
        yield org
    finally:
        try:
            await aiohttp_influx.delete_organization(organization_id=org.id)
        # allow only when org not exist
        except Exception:
            pass


@pytest.fixture(scope='function')
def bucket_name() -> str:
    return f'bucket-{random.random() * 100:.3f}'


@pytest_asyncio.fixture(scope='function')
async def bucket(
    aiohttp_influx: AioHTTPClient,
    organization: types.Organization,
    bucket_name: str,
) -> types.Bucket:
    return await aiohttp_influx.create_bucket(name=bucket_name, organization_id=organization.id)
