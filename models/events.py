from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel
from enums.event_actions import EventActions
from enums.job_type import JobType

class JobEvent(BaseModel):
    job_name: str
    action: Literal[EventActions]
    collector_name: str
    maas_pool_name: str
    job_type: Literal[JobType]
    data: Optional[Dict[str, Any]] = None
