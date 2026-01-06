from typing import List, Optional, Union, Annotated, Dict, Literal, Any
from beanie import Document
from pydantic import Field, ConfigDict
from datetime import datetime, timezone
from enums.blackbox_job_modules import BlackboxJobModules
from enums.job_type import JobType
from enums.kubernetes_roles import KubernetesRoles
from models.general.jobs.basic_auth import BasicAuth


class BaseJob(Document):
    job_name: str
    scrape_interval: Optional[int] = None
    scrape_timeout: Optional[int] = None
    basic_auth: Optional[BasicAuth] = None
    maas_pool: str
    labels: Optional[Dict[str, str]] = None
    collector_cluster: str
    time_created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    update_time: Optional[datetime] = Field(default=None)

    class Settings:
        name = "jobs"
        is_root = True
        allow_inheritance = True
        keep_nulls = False

    model_config = ConfigDict(
        populate_by_name=True
    )

    def to_event_data(self) -> Dict[str, Any]:
        return self.model_dump(
            mode="json",
            exclude={'maas_pool', 'collector_cluster', 'time_created', 'update_time', 'id', 'job_type'},
            exclude_none=True
        )

    @classmethod
    def get_child_class_ids(cls) -> List[str]:
        children = getattr(cls, "_children", {})
        ids = list(children.keys())
        ids.append("BaseJob")

        return ids

    
class GeneralJob(BaseJob):
    job_type: Literal[JobType.GENERAL] = JobType.GENERAL
    targets: List[str] = Field(...)
    metrics_path: Optional[str] = None
    certs: Optional[bool] = None

class BlackboxJob(BaseJob):
    job_type: Literal[JobType.BLACKBOX] = JobType.BLACKBOX
    targets: List[str] = Field(...)
    host: str
    module: BlackboxJobModules
    probe_path: Optional[str] = None

class KubernetesJob(BaseJob):
    job_type: Literal[JobType.KUBERNETES_SD] = JobType.KUBERNETES_SD
    namespaces: List[str]
    role: Optional[KubernetesRoles] = KubernetesRoles.POD
    metrics_path: Optional[str] = None

class HttpJob(BaseJob):
    job_type: Literal[JobType.HTTP_SD] = JobType.HTTP_SD
    endpoints: List[str]
    refresh_interval: Optional[int] = None
    metrics_path: Optional[str] = None
    certs: Optional[bool] = None


JobModel = Annotated[Union[GeneralJob, BlackboxJob, KubernetesJob, HttpJob], Field(discriminator="job_type")]