from typing import List

from fastapi import HTTPException

from enums.event_actions import EventActions
from enums.job_type import JobType
from exceptions.collector_not_in_pool_error import CollectorNotInPoolError
from exceptions.job_name_exists_error import JobNameExistsError
from exceptions.job_not_exist_error import JobNotExistsError
from exceptions.produce_failure_error import ProduceFailureError
from exceptions.unauthorized_api_key import UnauthorizedApiKeyError
from models.db_schemas.jobs import (
    BlackboxJob,
    GeneralJob,
    HttpJob,
    JobModel,
    KubernetesJob,
)
from models.general.jobs.labels import JobLabels
from models.response_schemas.response_detail import ResponseDetail
from models.validation_schemas.create_schemas.jobs import BaseJobCreate
from models.validation_schemas.update_schemas.jobs import BaseJobUpdate
from producer import producer
from repositories.job_repository import JobRepository
from repositories.pool_repository import PoolRepository
from services.base_service import BaseService
from services.pool_service import PoolService
from utils.logger import create_logger
from utils.security import security_manager

logger = create_logger("job_service")


class JobService(BaseService[JobModel, JobRepository]):
    def __init__(self, repo: JobRepository, pool_repo: PoolRepository):
        super().__init__(repo)
        self.pool_service = PoolService(pool_repo)

    @staticmethod
    def _check_if_authorized(
        authorized_pools: List[str], maas_pool: str, is_admin: bool
    ):
        if not is_admin and maas_pool not in authorized_pools:
            logger.warning(f"API key is not authorized for {maas_pool}")
            raise UnauthorizedApiKeyError(maas_pool=maas_pool)

    async def get(
        self,
        job_name: str,
        maas_pool: str,
        collector_cluster: str,
        authorized_pools: List[str],
        is_admin: bool,
    ):
        self._check_if_authorized(authorized_pools, maas_pool, is_admin)
        job = await self.repo.get(
            job_name=job_name, maas_pool=maas_pool, collector_cluster=collector_cluster
        )

        if not job:
            logger.warning(f"Job {job_name} not found")
            raise JobNotExistsError(job_name=job_name, collector_name=collector_cluster)

        if job.basic_auth:
            job.basic_auth.password = "*****"

        return job

    async def create(
        self, job: BaseJobCreate, authorized_pools: List[str], is_admin: bool
    ) -> ResponseDetail:
        self._check_if_authorized(authorized_pools, job.maas_pool, is_admin)

        if not await self.pool_service.check_collector_in_pool(
            job.maas_pool, job.collector_cluster
        ):
            logger.warning(
                f"Collector {job.collector_cluster} not found in pool {job.maas_pool}"
            )
            raise CollectorNotInPoolError(
                maas_pool=job.maas_pool, collector_cluster=job.collector_cluster
            )

        if await self.repo.get(
            job_name=job.job_name,
            maas_pool=job.maas_pool,
            collector_cluster=job.collector_cluster,
        ):
            logger.warning(f"Job {job.job_name} already exists")
            raise JobNameExistsError(
                job_name=job.job_name, collector_cluster=job.collector_cluster
            )

        job_model = {
            JobType.GENERAL: GeneralJob,
            JobType.BLACKBOX: BlackboxJob,
            JobType.KUBERNETES_SD: KubernetesJob,
            JobType.HTTP_SD: HttpJob,
        }.get(job.job_type)

        if job_model is None:
            logger.warning(f"Job type {job.job_type} is not supported")
            raise ValueError(f"Job type {job.job_type} is not supported")

        if job.basic_auth:
            job.basic_auth.password = security_manager.encrypt(job.basic_auth.password)

        db_job = job_model(**job.model_dump())
        await self.repo.create(db_job)

        try:
            await producer.send_event(
                EventActions.CREATE,
                job.maas_pool,
                job.collector_cluster,
                job.job_type,
                job.job_name,
                job.model_dump(),
            )
            logger.info(f"Job {job.job_name} created successfully")
            return ResponseDetail(detail=f"Job {job.job_name} created successfully")
        except ProduceFailureError as e:
            logger.error(f"Failed to create job {job.job_name}: {str(e)}")
            await self.repo.delete(db_job)
            raise e

    async def update(
        self,
        job_name: str,
        maas_pool: str,
        job: BaseJobUpdate,
        collector_cluster: str,
        authorized_pools: List[str],
        is_admin: bool,
    ) -> ResponseDetail:
        self._check_if_authorized(authorized_pools, maas_pool, is_admin)

        existing_job = await self.get(
            job_name, maas_pool, collector_cluster, authorized_pools, is_admin
        )
        original_dump = existing_job.model_dump()
        update_data = job.model_dump(exclude_unset=True)

        if update_data.get("basis_auth"):
            update_data["basis_auth"]["password"] = security_manager.encrypt(
                update_data["basis_auth"]["password"]
            )

        await self.repo.update(existing_job, update_data)

        try:
            await producer.send_event(
                EventActions.UPDATE,
                existing_job.maas_pool,
                existing_job.collector_cluster,
                existing_job.job_type,
                existing_job.job_name,
                update_data,
            )
            logger.info(f"Job {job.job_name} updated successfully")
            return ResponseDetail(detail=f"Job {job.job_name} updated successfully")
        except ProduceFailureError as e:
            logger.error(f"Failed to update job {job.job_name}: {str(e)}")
            await self.repo.update(existing_job, original_dump)
            raise e

    async def delete(
        self,
        job_name: str,
        maas_pool: str,
        collector_cluster: str,
        authorized_pools: List[str],
        is_admin: bool,
    ) -> ResponseDetail:
        self._check_if_authorized(authorized_pools, maas_pool, is_admin)

        job = await self.get(
            job_name, maas_pool, collector_cluster, authorized_pools, is_admin
        )
        job_backup = job.model_dump()
        await self.repo.delete(job)

        try:
            await producer.send_event(
                EventActions.DELETE,
                job.maas_pool,
                job.collector_cluster,
                job.job_type,
                job.job_name,
                job_backup,
            )
            logger.info(f"Job {job.job_name} deleted successfully")
            return ResponseDetail(detail=f"Job {job.job_name} deleted successfully")
        except ProduceFailureError as e:
            logger.error(f"Failed to delete job {job.job_name}: {str(e)}")
            new_doc = type(job)(**job_backup)
            await self.repo.create(new_doc)
            raise e

    async def add_target(
        self,
        job_name: str,
        maas_pool: str,
        collector_cluster: str,
        target: str,
        authorized_pools: List[str],
        is_admin: bool,
    ) -> ResponseDetail:
        self._check_if_authorized(authorized_pools, maas_pool, is_admin)

        job = await self.get(
            job_name, maas_pool, collector_cluster, authorized_pools, is_admin
        )

        if not hasattr(job, "targets"):
            raise HTTPException(status_code=400, detail="Job does not support targets")

        if target not in job.targets:
            job.targets.append(target)
            await self.repo.save(job)

            try:
                await producer.send_event(
                    EventActions.UPDATE,
                    job.maas_pool,
                    job.collector_cluster,
                    job.job_type,
                    job.job_name,
                    job.model_dump(),
                )
                logger.info(f"Target {target} added to job {job.job_name} successfully")
                return ResponseDetail(
                    detail=f"Target {target} added to job {job.job_name} successfully"
                )
            except ProduceFailureError as e:
                logger.error(
                    f"Failed to add target {target} to job {job.job_name}: {str(e)}"
                )
                job.targets.remove(target)
                await self.repo.save(job)
                raise e

    async def delete_target(
        self,
        job_name: str,
        maas_pool: str,
        collector_cluster: str,
        target: str,
        authorized_pools: List[str],
        is_admin: bool,
    ) -> ResponseDetail:
        self._check_if_authorized(authorized_pools, maas_pool, is_admin)

        job = await self.get(
            job_name, maas_pool, collector_cluster, authorized_pools, is_admin
        )

        if not hasattr(job, "targets"):
            raise HTTPException(status_code=400, detail="Job does not support targets")

        if target in job.targets:
            job.targets.remove(target)
            await self.repo.save(job)

            try:
                await producer.send_event(
                    EventActions.UPDATE,
                    job.maas_pool,
                    job.collector_cluster,
                    job.job_type,
                    job.job_name,
                    job.model_dump(),
                )
                logger.info(
                    f"Target {target} deleted from job {job.job_name} successfully"
                )
                return ResponseDetail(
                    detail=f"Target {target} deleted from job {job.job_name} successfully"
                )
            except ProduceFailureError as e:
                logger.error(
                    f"Failed to delete target {target} from job {job.job_name}: {str(e)}"
                )
                job.targets.append(target)
                await self.repo.save(job)
                raise e

    async def add_label(
        self,
        job_name: str,
        maas_pool: str,
        collector_cluster: str,
        labels: JobLabels,
        authorized_pools: List[str],
        is_admin: bool,
    ) -> ResponseDetail:
        self._check_if_authorized(authorized_pools, maas_pool, is_admin)

        job = await self.get(
            job_name, maas_pool, collector_cluster, authorized_pools, is_admin
        )

        if not job.labels:
            job.labels = {}

        original_labels = job.labels.copy()
        job.labels.update(labels)
        await self.repo.save(job)

        try:
            await producer.send_event(
                EventActions.UPDATE,
                job.maas_pool,
                job.collector_cluster,
                job.job_type,
                job.job_name,
                job.model_dump(),
            )
            logger.info(f"Label {labels} added to job {job.job_name} successfully")
            return ResponseDetail(
                detail=f"Label {labels} added to job {job.job_name} successfully"
            )
        except ProduceFailureError as e:
            logger.error(
                f"Failed to add label {labels} to job {job.job_name}: {str(e)}"
            )
            job.labels = original_labels
            await self.repo.save(job)
            raise e

    async def update_label(
        self,
        job_name: str,
        maas_pool: str,
        collector_cluster: str,
        label_key: str,
        label_value: str,
        authorized_pools: List[str],
        is_admin: bool,
    ) -> ResponseDetail:
        self._check_if_authorized(authorized_pools, maas_pool, is_admin)

        job = await self.get(
            job_name, maas_pool, collector_cluster, authorized_pools, is_admin
        )

        if job.labels is None or label_key not in job.labels:
            raise HTTPException(status_code=400, detail="Label not found")

        original_labels = job.labels.copy()
        job.labels[label_key] = label_value
        await self.repo.save(job)

        try:
            await producer.send_event(
                EventActions.UPDATE,
                job.maas_pool,
                job.collector_cluster,
                job.job_type,
                job.job_name,
                job.model_dump(),
            )
            logger.info(f"Label {label_key} updated to job {job.job_name} successfully")
            return ResponseDetail(
                detail=f"Label {label_key} updated to job {job.job_name} successfully"
            )
        except ProduceFailureError as e:
            logger.error(
                f"Failed to update label {label_key} to job {job.job_name}: {str(e)}"
            )
            job.labels = original_labels
            await self.repo.save(job)
            raise e

    async def delete_label(
        self,
        job_name: str,
        maas_pool: str,
        collector_cluster: str,
        label_key: str,
        authorized_pools: List[str],
        is_admin: bool,
    ) -> ResponseDetail:
        self._check_if_authorized(authorized_pools, maas_pool, is_admin)

        job = await self.get(
            job_name, maas_pool, collector_cluster, authorized_pools, is_admin
        )

        if job.labels and label_key in job.labels:
            original_labels = job.labels.copy()
            del job.labels[label_key]
            await self.repo.save(job)

            try:
                await producer.send_event(
                    EventActions.UPDATE,
                    job.maas_pool,
                    job.collector_cluster,
                    job.job_type,
                    job.job_name,
                    job.model_dump(),
                )
                logger.info(
                    f"Label {label_key} deleted from job {job.job_name} successfully"
                )
                return ResponseDetail(
                    detail=f"Label {label_key} deleted from job {job.job_name} successfully"
                )
            except ProduceFailureError as e:
                logger.error(
                    f"Failed to delete label {label_key} from job {job.job_name}: {str(e)}"
                )
                job.labels = original_labels
                await self.repo.save(job)
                raise e
