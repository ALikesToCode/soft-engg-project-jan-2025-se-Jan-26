import pytest

@pytest.mark.asyncio
async def test_simple():
    """A simple test that doesn't rely on any fixtures."""
    assert True 