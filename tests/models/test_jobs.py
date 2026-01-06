
import pytest
from pydantic import TypeAdapter
from models.db_schemas.jobs import JobModel, GeneralJob, BlackboxJob
from enums.job_type import JobType

@pytest.mark.asyncio
async def test_job_polymorphism(init_beanie_db):
    # Test that JobModel correctly discriminates based on job_type
    
    general_data = {
        "job_name": "gen-job",
        "maas_pool": "pool1",
        "collector_cluster": "col1",
        "job_type": JobType.GENERAL,
        "targets": ["localhost:9090"]
    }
    
    # Use TypeAdapter for standard Pydantic v2 validation of Annotated Union
    job = TypeAdapter(JobModel).validate_python(general_data)
    assert isinstance(job, GeneralJob)
    assert job.job_type == JobType.GENERAL
    
    bb_data = {
        "job_name": "bb-job",
        "maas_pool": "pool1",
        "collector_cluster": "col1",
        "job_type": JobType.BLACKBOX,
        "targets": ["localhost:9090"],
        "host": "example.com",
        "module": "http_2xx"
    }
    
    job_bb = TypeAdapter(JobModel).validate_python(bb_data)
    assert isinstance(job_bb, BlackboxJob)
    assert job_bb.job_type == JobType.BLACKBOX

@pytest.mark.asyncio
async def test_job_defaults(init_beanie_db):
    data = {
        "job_name": "def-job",
        "maas_pool": "pool1",
        "collector_cluster": "col1",
        "job_type": JobType.GENERAL,
        "targets": ["localhost:9090"]
    }
    # Direct instantiation checks default_factory logic
    job = GeneralJob(**data)
    assert job.scrape_interval is None 
    assert job.time_created is not None
