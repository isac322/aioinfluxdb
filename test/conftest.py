from __future__ import annotations

import os
from dataclasses import dataclass

import pytest


@dataclass(frozen=True)
class InfluxDBConfig:
    host: str
    port: int
    username: str
    password: str
    org: str
    bucket: str
    admin_token: str


@pytest.fixture(scope='session')
def influxdb_config() -> InfluxDBConfig:
    return InfluxDBConfig(
        host=os.environ['INFLUXDB_HOST'],
        port=os.environ.get('INFLUXDB_PORT', 8086),
        username=os.environ['INFLUXDB_USERNAME'],
        password=os.environ['INFLUXDB_PASSWORD'],
        org=os.environ['INFLUXDB_ORG'],
        bucket=os.environ['INFLUXDB_BUCKET'],
        admin_token=os.environ['INFLUXDB_ADMIN_TOKEN'],
    )
