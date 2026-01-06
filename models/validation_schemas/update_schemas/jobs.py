from pydantic import BaseModel, Field, field_validator, ValidationInfo
from typing import Optional, Literal, Any
from config.constants.jobs import JOB_NAME_REGEX, MIN_REFRESH_INTERVAL, MIN_SCRAPE_INTERVAL, MIN_SCRAPE_TIMEOUT, MAX_REFRESH_INTERVAL, MAX_SCRAPE_INTERVAL, MAX_SCRAPE_TIMEOUT, METRICS_PATH_REGEX, HOST_REGEX
from enums.job_type import JobType
from enums.blackbox_job_modules import BlackboxJobModules
from models.general.jobs.basic_auth import BasicAuth
from models.general.jobs.endpoints import JobEndpoints
from models.general.jobs.labels import JobLabels
from models.general.jobs.namespaces import JobNamespaces
from models.general.jobs.targets import JobTargets
from enums.kubernetes_roles import KubernetesRoles


class BaseJobUpdate(BaseModel):
    job_name: Optional[str] = Field(default=None, pattern=JOB_NAME_REGEX) 
    scrape_interval: Optional[int] = Field(default=None, ge=MIN_SCRAPE_INTERVAL, le=MAX_SCRAPE_INTERVAL)
    scrape_timeout: Optional[int] = Field(default=None, ge=MIN_SCRAPE_TIMEOUT, le=MAX_SCRAPE_TIMEOUT)
    basic_auth: Optional[BasicAuth] = Field(default=None)
    labels: Optional[JobLabels] = Field(default=None)

    @field_validator('job_name')
    @classmethod
    def validate_base_mandatory_fields(cls, v: Any, info: ValidationInfo):
        """prevent the user from explicitly entering null on mandatory fields"""
        if v is None:
            raise ValueError("Mandatory field cannot be null")
        
        return v


class GeneralJobUpdate(BaseJobUpdate):
    job_type: Literal[JobType.GENERAL] = Field(default=JobType.GENERAL)
    targets: Optional[JobTargets] = Field(default=None)
    metrics_path: Optional[str] = Field(default=None, pattern=METRICS_PATH_REGEX)
    certs: Optional[bool] = Field(default=None)

    @field_validator('targets')
    @classmethod
    def validate_targets(cls, v: Any, info: ValidationInfo):
        """prevent the user from explicitly entering null on mandatory fields"""
        if v is None:
            raise ValueError("Mandatory field cannot be null")
        
        return v


class BlackboxJobUpdate(BaseJobUpdate):
    job_type: Literal[JobType.BLACKBOX] = Field(default=JobType.BLACKBOX)
    targets: Optional[JobTargets] = Field(default=None)
    module: Optional[BlackboxJobModules] = Field(default=None)
    host: Optional[str] = Field(default=None, pattern=HOST_REGEX)
    probe_path: Optional[str] = Field(default=None, pattern=METRICS_PATH_REGEX)

    @field_validator('targets', 'module', 'probe_path', 'module')
    @classmethod
    def validate_targets(cls, v: Any, info: ValidationInfo):
        """prevent the user from explicitly entering null on mandatory fields"""
        if v is None:
            raise ValueError("Mandatory field cannot be null")
        
        return v


class KubernetesSDJobUpdate(BaseJobUpdate):
    job_type: Literal[JobType.KUBERNETES_SD] = Field(default=JobType.KUBERNETES_SD)
    namespace: Optional[JobNamespaces] = Field(default=None)
    role: Optional[KubernetesRoles] = Field(default=None)
    metrics_path: Optional[str] = Field(default=None, pattern=METRICS_PATH_REGEX)

    @field_validator('namespace')
    @classmethod
    def validate_namespace(cls, v: Any, info: ValidationInfo):
        """prevent the user from explicitly entering null on mandatory fields"""
        if v is None:
            raise ValueError("Mandatory field cannot be null")
        
        return v

class HttpJobUpdate(BaseJobUpdate):
    job_type: Literal[JobType.HTTP_SD] = Field(default=JobType.HTTP_SD)
    endpoints: Optional[JobEndpoints] = Field(default=None)
    metrics_path: Optional[str] = Field(default=None, pattern=METRICS_PATH_REGEX)
    refresh_interval: Optional[int] = Field(default=None, ge=MIN_REFRESH_INTERVAL, le=MAX_REFRESH_INTERVAL)
    certs: Optional[bool] = Field(default=None)

    @field_validator('endpoints')
    @classmethod
    def validate_endpoints(cls, v: Any, info: ValidationInfo):
        """prevent the user from explicitly entering null on mandatory fields"""
        if v is None:
            raise ValueError("Mandatory field cannot be null")
        
        return v
