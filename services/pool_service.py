from models.db_schemas.maas_pools import MaasPool
from repositories.pool_repository import PoolRepository
from services.base_service import BaseService
from exceptions.pool_not_exist_error import PoolNotExistsError


class PoolService(BaseService[MaasPool, PoolRepository]):
    async def get(self, maas_pool: str) -> MaasPool:
        pool = await self.repo.get(name=maas_pool)

        if not pool:
            raise PoolNotExistsError(maas_pool=maas_pool)

        return pool
    
    async def check_collector_in_pool(self, maas_pool: str, collector_cluster: str) -> bool:
        pool = await self.get(maas_pool)
        return collector_cluster in pool.collector_clusters
    


