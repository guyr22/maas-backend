from typing import Optional, List
from fastapi import APIRouter, Depends, Body
from models.db_schemas.api_keys import ApiKey
from utils.authorization import get_admin_api_key, get_api_key_service
from services.api_key_service import APIKeyService
from models.response_schemas.api_keys import ApiKeyResponse

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/api-key", response_model=ApiKeyResponse)
async def create_api_key(maas_pools: List[str] = Body(..., embed=True),
                        is_admin: bool = Body(..., embed=True),
                        description: Optional[str] = Body(None, embed=True),
                        service: APIKeyService = Depends(get_api_key_service),
                        admin_key: ApiKey = Depends(get_admin_api_key)):
    return await service.create_key(maas_pools, description, is_admin)


@router.post("/api-key/{key}/{maas_pool}")
async def add_pool_to_key(key: str, maas_pool: str, service: APIKeyService = Depends(get_api_key_service),
                        admin_key: ApiKey = Depends(get_admin_api_key)):
    return await service.add_pool(key, maas_pool)


@router.delete("/api-key/{key}/{maas_pool}")
async def revoke_key_from_pool(key: str, maas_pool: str, service: APIKeyService = Depends(get_api_key_service),
                        admin_key: ApiKey = Depends(get_admin_api_key)):
    return await service.revoke_key_from_pool(key, maas_pool)


@router.delete("/api-key/{key}")
async def revoke_key(key: str, service: APIKeyService = Depends(get_api_key_service),
                        admin_key: ApiKey = Depends(get_admin_api_key)):
    return await service.revoke_key(key)

    
