from typing import Optional, Dict, Any
from datetime import datetime, timezone
from repositories.base_repository import BaseRepository
from models.db_schemas.jobs import BaseJob


class JobRepository(BaseRepository[BaseJob]):
    def __init__(self):
        super().__init__(BaseJob)

    async def create(self, document: BaseJob) -> BaseJob:
        return await document.create()

    async def get(self, job_name: str, maas_pool: str, collector_cluster: str) -> Optional[BaseJob]:
        query: Dict[str, Any] = {
            'job_name': job_name,
            'maas_pool': maas_pool,
            'collector_cluster': collector_cluster
        }

        children_ids = list(BaseJob.get_child_class_ids())
        query['_class_id'] = {'$in': children_ids}

        return await self.model.find_one(query)

    async def update(self, document: BaseJob, data: Dict[str, Any]) -> BaseJob:
        data['update_time'] = datetime.now(timezone.utc)
        await document.set(data)
        return document

    async def delete(self, document: BaseJob) -> BaseJob:
        await document.delete()

    @staticmethod
    async def save(document: BaseJob) -> BaseJob:
        document.update_time = datetime.now(timezone.utc)
        return await document.save()