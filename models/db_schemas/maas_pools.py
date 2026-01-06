from typing import Optional, List
from datetime import datetime, timezone
from pydantic import Field
from beanie import Document


class MaasPool(Document):
    name: str = Field(...)
    collectors: List[str] = Field(default=[])
    clusters: List[str] = Field(default=[])
    time_created: datetime = Field(default_factory=datetime.now(timezone.utc))
    update_time: Optional[datetime] = Field(default=None)

    class Settings:
        name = "maas_pools"