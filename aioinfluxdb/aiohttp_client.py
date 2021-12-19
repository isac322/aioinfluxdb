from __future__ import annotations

import http
from typing import Optional

import aiohttp

from aioinfluxdb.client import Client


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
    ) -> None:
        super().__init__(token)

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

    async def close(self) -> None:
        await self._session.close()
