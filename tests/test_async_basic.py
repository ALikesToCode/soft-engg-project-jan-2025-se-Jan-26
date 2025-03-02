import pytest
import asyncio

@pytest.mark.anyio
async def test_async_basic():
    """A simple async test to check if anyio is working"""
    await asyncio.sleep(0.1)
    assert 1 + 1 == 2 