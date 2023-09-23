"""Module pytest fixtures."""

from typing import AsyncIterator

import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient

from hook.main import app


@pytest.fixture
def anyio_backend():
    """Set pytest anyio backend to asyncio."""
    return "asyncio"


@pytest.fixture
@pytest.mark.anyio
async def client() -> AsyncIterator[AsyncClient]:
    """Yield an asynchronous HTTP client for the FastAPI app."""
    async with LifespanManager(app) as manager:
        async with AsyncClient(app=manager.app, base_url="http://test") as aclient:
            yield aclient
