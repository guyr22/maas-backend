from typing import Optional, Literal
from pydantic import BaseModel, Field
from config.constants.jobs import JOB_NAME_REGEX, MIN_REFRESH_INTERVAL, MIN_SCRAPE_INTERVAL, MIN_SCRAPE_TIMEOUT, MAX_REFRESH_INTERVAL, MAX_SCRAPE_INTERVAL, MAX_SCRAPE_TIMEOUT, COLLECTOR_CLUSTER_REGEX, MAAS_POOL_NAME_REGEX, METRICS_PATH_REGEX, HOST_REGEX
from enums.job_type import JobType
from enums.blackbox_job_modules import BlackboxJobModules
from enums.kubernetes_roles import KubernetesRoles
from models.general.jobs.basic_auth import BasicAuth
from models.general.jobs.endpoints import JobEndpoints
from models.general.jobs.labels import JobLabels
from models.general.jobs.namespaces import JobNamespaces
from models.general.jobs.targets import JobTargets


class BaseJobCreate(BaseModel):
    job_name: str = Field(..., pattern=JOB_NAME_REGEX) 
    scrape_interval: Optional[int] = Field(default=None, ge=MIN_SCRAPE_INTERVAL, le=MAX_SCRAPE_INTERVAL)
    scrape_timeout: Optional[int] = Field(default=None, ge=MIN_SCRAPE_TIMEOUT, le=MAX_SCRAPE_TIMEOUT)
    basic_auth: Optional[BasicAuth] = Field(default=None)
    labels: Optional[JobLabels] = Field(default=None)
    collector_cluster: str = Field(..., pattern=COLLECTOR_CLUSTER_REGEX)
    maas_pool: str = Field(..., pattern=MAAS_POOL_NAME_REGEX)


class GeneralJobCreate(BaseJobCreate):
    job_type: Literal[JobType.GENERAL] = Field(default=JobType.GENERAL)
    targets: JobTargets = Field(...)
    metrics_path: Optional[str] = Field(default=None, pattern=METRICS_PATH_REGEX)
    certs: Optional[bool] = Field(default=None)


class BlackboxJobCreate(BaseJobCreate):
    job_type: Literal[JobType.BLACKBOX] = Field(default=JobType.BLACKBOX)
    targets: JobTargets = Field(...)
    module: BlackboxJobModules = Field(...)
    host: str = Field(..., pattern=HOST_REGEX)
    probe_path: str = Field(..., pattern=METRICS_PATH_REGEX)


class KubernetesSDJobCreate(BaseJobCreate):
    job_type: Literal[JobType.KUBERNETES_SD] = Field(default=JobType.KUBERNETES_SD)
    namespace: JobNamespaces = Field(...)
    role: KubernetesRoles = Field(...)
    metrics_path: Optional[str] = Field(default=None, pattern=METRICS_PATH_REGEX)


class HttpJobCreate(BaseJobCreate):
    job_type: Literal[JobType.HTTP_SD] = Field(default=JobType.HTTP_SD)
    endpoints: JobEndpoints = Field(...)
    metrics_path: Optional[str] = Field(default=None, pattern=METRICS_PATH_REGEX)
    refresh_interval: Optional[int] = Field(default=None, ge=MIN_REFRESH_INTERVAL, le=MAX_REFRESH_INTERVAL)
    certs: Optional[bool] = Field(default=None)
    
