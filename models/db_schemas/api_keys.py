import re
from typing import Optional, List
from datetime import datetime, timezone
from pydantic import Field, model_validator
from beanie import Document, Indexed
from config.constants.jobs import MAAS_POOL_NAME_REGEX


class ApiKey(Document):
    key: Indexed(str) = Field(...)
    maas_pools: List[str] = Field(default=[])
    description: Optional[str] = Field(default=None)
    time_created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_admin: bool = Field(default=False)

    @model_validator(mode="after")
    def validate_maas_pools(self):
        if self.maas_pools:
            pattern = re.compile(MAAS_POOL_NAME_REGEX)
            for maas_pool in self.maas_pools:
                if not pattern.match(maas_pool):
                    raise ValueError(f"Invalid maas pool name: {maas_pool}")
        return self

    class Settings:
        name = "api_keys"