from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ApiKeyResponse(BaseModel):
    key: str
    maas_pools: List[str]
    description: Optional[str] = None
    time_created: datetime