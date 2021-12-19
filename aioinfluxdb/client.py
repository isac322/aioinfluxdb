from __future__ import annotations

import asyncio
from abc import ABCMeta, abstractmethod


class Client(metaclass=ABCMeta):
    _token: str

    def __init__(self, token: str) -> None:
        self._token = token

    def __del__(self) -> None:
        asyncio.create_task(self.close())

    @abstractmethod
    async def ping(self) -> bool:
        """`true` if pong received"""
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError

    @property
    def api_token(self):
        return self._token
