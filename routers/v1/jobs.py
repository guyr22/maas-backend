from fastapi import APIRouter, Depends
from models.db_schemas.api_keys import ApiKey
from models.general.jobs.labels import JobLabels
from models.response_schemas.response_detail import ResponseDetail
from models.validation_schemas.create_schemas.jobs import GeneralJobCreate, BlackboxJobCreate, HttpJobCreate, KubernetesJobCreate
from models.validation_schemas.update_schemas.jobs import GeneralJobUpdate, BlackboxJobUpdate, HttpJobUpdate, KubernetesJobUpdate
from models.db_schemas.jobs import JobModel
from repositories.job_repository import JobRepository
from repositories.pool_repository import PoolRepository
from services.job_service import JobService
from utils.authorization import get_api_key
from utils.security import SecurityManager
from config import config


router = APIRouter(prefix="/jobs", tags=["Jobs"])


async def get_pool_repo() -> PoolRepository:
    return PoolRepository()


async def get_job_repo() -> JobRepository:
    return JobRepository()


async def get_security_manager() -> SecurityManager:
    return SecurityManager(config["security"]["secret_key"])


async def get_job_service(repo: JobRepository = Depends(get_job_repo), pool_repo: PoolRepository = Depends(get_pool_repo), security_manager: SecurityManager = Depends(get_security_manager)) -> JobService:
    return JobService(repo, pool_repo, security_manager)


@router.get("/{job_name}", response_model=JobModel, response_model_exclude_none=True)
async def get_job(job_name: str, maas_pool: str, collector_cluster: str, service: JobService = Depends(get_job_service), api_key: ApiKey = Depends(get_api_key)):
    return await service.get(job_name, maas_pool, collector_cluster, api_key.maas_pools, api_key.is_admin)


@router.delete("/{job_name}", response_model=ResponseDetail)
async def delete_job(job_name: str, maas_pool: str, collector_cluster: str, service: JobService = Depends(get_job_service), api_key: ApiKey = Depends(get_api_key)):
    return await service.delete(job_name, maas_pool, collector_cluster, api_key.maas_pools, api_key.is_admin)


@router.post(path="/general/", response_model=ResponseDetail)
async def create_general_job(job: GeneralJobCreate, service: JobService = Depends(get_job_service), api_key: ApiKey = Depends(get_api_key)):
    return await service.create(job, api_key.maas_pools, api_key.is_admin)


@router.put(path="/general/{job_name}", response_model=ResponseDetail)
async def update_general_job(job_name: str, job: GeneralJobUpdate, maas_pool: str, collector_cluster: str, service: JobService = Depends(get_job_service), api_key: ApiKey = Depends(get_api_key)):
    return await service.update(job_name, maas_pool, job, collector_cluster, api_key.maas_pools, api_key.is_admin)


@router.post(path="/general/{job_name}/target", response_model=ResponseDetail)
async def add_general_job_target(job_name: str, target: str, maas_pool: str, collector_cluster: str, service: JobService = Depends(get_job_service), api_key: ApiKey = Depends(get_api_key)):
    return await service.add_target(job_name, maas_pool, collector_cluster, target, api_key.maas_pools, api_key.is_admin)


@router.delete(path="/general/{job_name}/target", response_model=ResponseDetail)
async def remove_general_job_target(job_name: str, target: str, maas_pool: str, collector_cluster: str, service: JobService = Depends(get_job_service), api_key: ApiKey = Depends(get_api_key)):
    return await service.delete_target(job_name, maas_pool, collector_cluster, target, api_key.maas_pools, api_key.is_admin)


@router.post(path="/blackbox/", response_model=ResponseDetail)
async def create_blackbox_job(job: BlackboxJobCreate, service: JobService = Depends(get_job_service), api_key: ApiKey = Depends(get_api_key)):
    return await service.create(job, api_key.maas_pools, api_key.is_admin)


@router.put(path="/blackbox/{job_name}", response_model=ResponseDetail)
async def update_blackbox_job(job_name: str, job: BlackboxJobUpdate, maas_pool: str, collector_cluster: str, service: JobService = Depends(get_job_service), api_key: ApiKey = Depends(get_api_key)):
    return await service.update(job_name, maas_pool, job, collector_cluster, api_key.maas_pools, api_key.is_admin)


@router.post(path="/blackbox/{job_name}/target", response_model=ResponseDetail)
async def add_blackbox_job_target(job_name: str, target: str, maas_pool: str, collector_cluster: str, service: JobService = Depends(get_job_service), api_key: ApiKey = Depends(get_api_key)):
    return await service.add_target(job_name, maas_pool, collector_cluster, target, api_key.maas_pools, api_key.is_admin)


@router.delete(path="/blackbox/{job_name}/target", response_model=ResponseDetail)
async def remove_blackbox_job_target(job_name: str, target: str, maas_pool: str, collector_cluster: str, service: JobService = Depends(get_job_service), api_key: ApiKey = Depends(get_api_key)):
    return await service.delete_target(job_name, maas_pool, collector_cluster, target, api_key.maas_pools, api_key.is_admin)


@router.post(path="/http/", response_model=ResponseDetail)
async def create_http_job(job: HttpJobCreate, service: JobService = Depends(get_job_service), api_key: ApiKey = Depends(get_api_key)):
    return await service.create(job, api_key.maas_pools, api_key.is_admin)


@router.put(path="/http/{job_name}", response_model=ResponseDetail)
async def update_http_job(job_name: str, job: HttpJobUpdate, maas_pool: str, collector_cluster: str, service: JobService = Depends(get_job_service), api_key: ApiKey = Depends(get_api_key)):
    return await service.update(job_name, maas_pool, job, collector_cluster, api_key.maas_pools, api_key.is_admin)


@router.post(path="/kubernetes/", response_model=ResponseDetail)
async def create_kubernetes_job(job: KubernetesJobCreate, service: JobService = Depends(get_job_service), api_key: ApiKey = Depends(get_api_key)):
    return await service.create(job, api_key.maas_pools, api_key.is_admin)


@router.put(path="/kubernetes/{job_name}", response_model=ResponseDetail)
async def update_kubernetes_job(job_name: str, job: KubernetesJobUpdate, maas_pool: str, collector_cluster: str, service: JobService = Depends(get_job_service), api_key: ApiKey = Depends(get_api_key)):
    return await service.update(job_name, maas_pool, job, collector_cluster, api_key.maas_pools, api_key.is_admin)


@router.post(path="/{job_name}/labels", response_model=ResponseDetail)
async def add_job_label(job_name: str, labels: JobLabels, maas_pool: str, collector_cluster: str, service: JobService = Depends(get_job_service), api_key: ApiKey = Depends(get_api_key)):
    return await service.add_label(job_name, maas_pool, collector_cluster, labels, api_key.maas_pools, api_key.is_admin)


@router.put(path="/{job_name}/labels", response_model=ResponseDetail)
async def update_job_label(job_name: str, label_key: str, label_value: str, maas_pool: str, collector_cluster: str, service: JobService = Depends(get_job_service), api_key: ApiKey = Depends(get_api_key)):
    return await service.update_label(job_name, maas_pool, collector_cluster, label_key, label_value, api_key.maas_pools, api_key.is_admin)


@router.delete(path="/{job_name}/labels", response_model=ResponseDetail)
async def delete_job_label(job_name: str, label_key: str, maas_pool: str, collector_cluster: str, service: JobService = Depends(get_job_service), api_key: ApiKey = Depends(get_api_key)):
    return await service.delete_label(job_name, maas_pool, collector_cluster, label_key, api_key.maas_pools, api_key.is_admin)
