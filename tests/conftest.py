import os
import sys

import pytest
from beanie import init_beanie
from mongomock_motor import AsyncMongoMockClient

# Add backend root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture(autouse=True)
def set_env_vars(monkeypatch):
    """Set environment variables for all tests using monkeypatch."""
    monkeypatch.setenv("SECRET_KEY", "BTzc1lV49sN6hmpQpUDIIKyZz-a5wwEskY_fsi6kGEDk=")
    monkeypatch.setenv("MONGO_CONNECTION_STRING", "mongodb://localhost:27017")
    monkeypatch.setenv("KAFKA_SERVERS", "localhost:9092")
    monkeypatch.setenv("KAFKA_TOPIC", "test-topic")
    monkeypatch.setenv("KAFKA_USERNAME", "user")
    monkeypatch.setenv("KAFKA_PASSWORD", "pass")
    monkeypatch.setenv("LOGSTASH_HOST", "localhost")
    monkeypatch.setenv("LOGSTASH_PORT", "5000")


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
