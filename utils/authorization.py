from typing import Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import APIKeyHeader
from services.api_key_service import APIKeyService
from repositories.api_key_repository import ApiKeyRepository
from models.db_schemas.api_keys import ApiKey

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key_repo() -> ApiKeyRepository:
    return ApiKeyRepository()

async def get_api_key_service(api_key_repo: ApiKeyRepository = Depends(get_api_key_repo)) -> APIKeyService:
    return APIKeyService(api_key_repo)


async def get_api_key(api_key: str = Depends(api_key_header),
                        service: APIKeyService = Depends(get_api_key_service)) -> Optional[ApiKey]:
    if not api_key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="API key is required")

    key_obj = await service.validate_key(api_key)

    return key_obj


async def get_admin_api_key(api_key: ApiKey = Depends(get_api_key)):
    if not api_key.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="API key is not authorized for admin actions")

    return api_key
