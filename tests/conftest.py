import os
import sys

import pytest
from beanie import init_beanie
from mongomock_motor import AsyncMongoMockClient

# Add backend root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture
async def init_beanie_db():
    # Import models here to ensure env vars are set before config is loaded
    from models.db_schemas.api_keys import ApiKey
    from models.db_schemas.jobs import (
        BaseJob,
        BlackboxJob,
        GeneralJob,
        HttpJob,
        KubernetesJob,
    )

    try:
        client = AsyncMongoMockClient()
        await init_beanie(
            database=client.test_db,
            document_models=[
                BaseJob,
                GeneralJob,
                BlackboxJob,
                KubernetesJob,
                HttpJob,
                ApiKey,
            ],
        )
    except Exception as e:
        print(f"Beanie initialization failed: {e}")
        raise
