from typing import Optional
from models.db_schemas.maas_pools import MaasPool
from repositories.base_repository import BaseRepository


class PoolRepository(BaseRepository):
    def __init__(self):
        super().__init__(MaasPool)

    async def create(self, document: MaasPool) -> MaasPool:
        return await document.create()

    async def get(self, name: str) -> Optional[MaasPool]:
        return await self.model.find_one(MaasPool.name == name)
