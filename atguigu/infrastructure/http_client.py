"""
定义Http客户端
IO/网络传输使用异步
同步、异步
"""

import asyncio
from httpx import AsyncClient

http_client: AsyncClient | None = None


def init_http_client():
    global http_client

    http_client = AsyncClient(timeout=120)


async def dispose_http_client():
    await http_client.aclose()
