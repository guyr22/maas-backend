
import pytest
from unittest.mock import AsyncMock
from services.api_key_service import APIKeyService
from models.db_schemas.api_keys import ApiKey
from fastapi import HTTPException

@pytest.fixture
def mock_repo():
    return AsyncMock()

@pytest.fixture
def api_key_service(mock_repo):
    service = APIKeyService(mock_repo)
    return service

@pytest.mark.asyncio
async def test_create_api_key(init_beanie_db, api_key_service: APIKeyService, mock_repo: AsyncMock):
    # Setup
    mock_saved_key = ApiKey(key="hashed_key", maas_pools=["maas-pool1"], is_admin=True)
    mock_repo.create.return_value = mock_saved_key
    
    # Execute
    response = await api_key_service.create_key(
        maas_pools=["maas-pool1"],
        description="test-key",
        is_admin=True
    )
    
    # Verify
    assert response.maas_pools == ["maas-pool1"]
    assert isinstance(response.key, str)
    assert len(response.key) > 0
    mock_repo.create.assert_called_once()
    
@pytest.mark.asyncio
async def test_revoke_api_key(init_beanie_db, api_key_service: APIKeyService, mock_repo: AsyncMock):
    # Setup
    mock_key = ApiKey(key="hash", maas_pools=["maas-pool1"], is_admin=True)
    mock_repo.get.return_value = mock_key
    
    # Execute
    await api_key_service.revoke_key("raw_key")
    
    # Verify
    mock_repo.delete.assert_called_once_with(mock_key)

@pytest.mark.asyncio
async def test_revoke_api_key_not_found(init_beanie_db, api_key_service: APIKeyService, mock_repo: AsyncMock):
    mock_repo.get.return_value = None
    
    with pytest.raises(HTTPException) as exc:
        await api_key_service.revoke_key("unknown")
    assert exc.value.status_code == 404
