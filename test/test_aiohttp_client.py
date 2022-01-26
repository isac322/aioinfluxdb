from __future__ import annotations

import pytest

from aioinfluxdb import AioHTTPClient, constants, types


@pytest.mark.asyncio
class TestAioHTTPClient:
    async def test_ping(self, aiohttp_client: AioHTTPClient) -> None:
        assert await aiohttp_client.ping() is True

    async def test_list_organizations(self, aiohttp_client: AioHTTPClient, organization: types.Organization) -> None:
        orgs = tuple(await aiohttp_client.list_organizations(organization_name=organization.name))
        assert len(orgs) == 1
        assert orgs[0].name == organization.name

    async def test_list_buckets(self, aiohttp_client: AioHTTPClient, bucket: types.Bucket) -> None:
        buckets = tuple(
            filter(
                lambda b: b.type is constants.BucketType.User,
                await aiohttp_client.list_buckets(organization_id=bucket.organization_id),
            )
        )
        assert len(buckets) == 1
        assert buckets[0].id == bucket.id
        assert buckets[0].name == bucket.name

    async def test_create_organization(self, aiohttp_client: AioHTTPClient, organization_name: str) -> None:
        org = await aiohttp_client.create_organization(name=organization_name)
        assert org.name == organization_name
        try:
            await aiohttp_client.delete_organization(organization_id=org.id)
        except Exception:
            pass

    async def test_delete_organization(self, aiohttp_client: AioHTTPClient, organization: types.Organization) -> None:
        await aiohttp_client.delete_organization(organization_id=organization.id)

    async def test_get_organization(self, aiohttp_client: AioHTTPClient, organization: types.Organization) -> None:
        org = await aiohttp_client.get_organization(organization_id=organization.id)
        assert org.id == organization.id
        assert org.name == organization.name

    async def test_create_bucket(
        self,
        aiohttp_client: AioHTTPClient,
        organization: types.Organization,
        bucket_name: str,
    ) -> None:
        bucket = await aiohttp_client.create_bucket(name=bucket_name, organization_id=organization.id)
        assert bucket.name == bucket_name
        try:
            await aiohttp_client.delete_bucket(bucket_id=bucket.id)
        except Exception:
            pass

    async def test_delete_bucket(self, aiohttp_client: AioHTTPClient, bucket: types.Bucket) -> None:
        await aiohttp_client.delete_bucket(bucket_id=bucket.id)

    async def test_get_bucket(self, aiohttp_client: AioHTTPClient, bucket: types.Bucket) -> None:
        b = await aiohttp_client.get_bucket(bucket_id=bucket.id)
        assert b.id == bucket.id
        assert b.name == bucket.name

    async def test_write(self, aiohttp_client: AioHTTPClient, bucket: types.Bucket) -> None:
        await aiohttp_client.write(
            bucket=bucket.id,
            organization_id=bucket.organization_id,
            record=('test', (('a', 1),)),
        )

    async def test_write_multiple(self, aiohttp_client: AioHTTPClient, bucket: types.Bucket) -> None:
        await aiohttp_client.write_multiple(
            bucket=bucket.id,
            organization_id=bucket.organization_id,
            records=(('test', (('a', 1),)), ('test', (('b', 2),))),
        )
