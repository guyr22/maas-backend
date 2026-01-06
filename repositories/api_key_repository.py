from models.db_schemas.api_keys import ApiKey
from repositories.base_repository import BaseRepository
from typing import Optional, Dict, Any

class ApiKeyRepository(BaseRepository):
    def __init__(self):
        super().__init__(ApiKey)

    async def create(self, document: ApiKey) -> ApiKey:
        return await document.create()

    async def get(self, key: str) -> Optional[ApiKey]:
        return await self.model.find_one(ApiKey.key == key)

    async def update(self, document: ApiKey, data: Dict[str, Any]) -> ApiKey:
        return await document.set(data)
        return document

    async def delete(self, document: ApiKey) -> ApiKey:
        return await document.delete()

    @staticmethod
    async def save(document: ApiKey) -> ApiKey:
        return await document.save()