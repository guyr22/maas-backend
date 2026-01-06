from models.response_schemas.api_keys import ApiKeyResponse
from models.response_schemas.response_detail import ResponseDetail
from models.db_schemas.api_keys import ApiKey
from repositories.api_key_repository import ApiKeyRepository
import hashlib
from exceptions.unauthorized_api_key import UnauthorizedApiKeyError
import secrets
from utils.logger import create_logger
from fastapi import HTTPException, status
from typing import List, Optional, Tuple

API_KEY_LENGTH = 32
logger = create_logger("api_key_service")


class APIKeyService:
    def __init__(self, repo: ApiKeyRepository):
        self.repo = repo

    def _hash(self, key: str) -> str:
        return hashlib.sha256(key.encode()).hexdigest()

    async def create_key(self, maas_pools: List[str], description: Optional[str] = None, is_admin: bool = False) -> Tuple[ApiKey, str]:
        raw_key = secrets.token_urlsafe(API_KEY_LENGTH)
        hashed_key = self._hash(raw_key)
        
        api_key = ApiKey(key=hashed_key, maas_pools=maas_pools, description=description, is_admin=is_admin)
        saved_key = await self.repo.create(api_key)
        
        return ApiKeyResponse(key=raw_key, maas_pools=saved_key.maas_pools, time_created=saved_key.time_created)

    async def validate_key(self, key: str) -> Optional[ApiKey]:
        hashed_key = self._hash(key)
        return await self.repo.get(hashed_key)

    async def revoke_key(self, key: str) -> ResponseDetail:
        db_key = await self.validate_key(key)

        if not db_key:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")

        await self.repo.delete(db_key)
        logger.info("API key revoked successfully")
        return ResponseDetail(detail="API key revoked successfully")

    async def revoke_key_from_pool(self, key: str, maas_pool: str) -> ResponseDetail:
        db_key = await self.validate_key(key)

        if not db_key or maas_pool not in db_key.maas_pools:
            raise UnauthorizedApiKeyError(maas_pool=maas_pool)

        db_key.maas_pools.remove(maas_pool)
        await self.repo.save(db_key)
        logger.info("API key revoked from pool successfully")
        return ResponseDetail(detail="API key revoked from pool successfully")

    async def add_pool(self, key: str, maas_pool: str) -> ResponseDetail:
        db_key = await self.validate_key(key)

        if not db_key or maas_pool in db_key.maas_pools:
            raise UnauthorizedApiKeyError(maas_pool=maas_pool)

        if maas_pool not in db_key.maas_pools:
            db_key.maas_pools.append(maas_pool)
            await self.repo.save(db_key)
            logger.info("API key added to pool successfully")

        return ResponseDetail(detail="API key added to pool successfully")
