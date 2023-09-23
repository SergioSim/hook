"""Hook API main entrypoint test."""

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_main_root(client: AsyncClient):
    """Test the main root route."""
    response = await client.get("/")
    assert response.json().get("username") == "admin"
