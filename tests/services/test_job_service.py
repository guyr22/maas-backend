
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from services.job_service import JobService
from enums.job_type import JobType
from models.db_schemas.jobs import GeneralJob
from models.validation_schemas.create_schemas.jobs import GeneralJobCreate
from exceptions.job_name_exists_error import JobNameExistsError
from utils.security import SecurityManager

@pytest.fixture
def mock_repo():
    return AsyncMock()

@pytest.fixture
def mock_pool_repo():
    return AsyncMock()


@pytest.fixture
def mock_security_manager():
    return AsyncMock()

@pytest.fixture
def job_service(mock_repo, mock_pool_repo, mock_security_manager):
    service = JobService(mock_repo, mock_pool_repo, mock_security_manager)
    mock_security_manager.encrypt.return_value = "encrypted_password"
    
    # Mock producer
    service.producer = AsyncMock()
    return service

@pytest.fixture
def security_manager():
    return SecurityManager("secret_key")

@pytest.mark.asyncio
async def test_create_job_success(init_beanie_db, job_service, mock_repo, mock_pool_repo):
    # Setup
    mock_pool_repo.get.return_value = MagicMock(collector_clusters=["ocp4-col1"])
    mock_repo.get.return_value = None # Job does not exist
    
    job_data = GeneralJobCreate(
        job_name="test-job",
        maas_pool="maas-pool1",
        collector_cluster="ocp4-col1",
        job_type=JobType.GENERAL,
        targets=["localhost:9090"]
    )
    
    # Execute
    with patch("services.job_service.producer") as mock_producer:
        mock_producer.send_event = AsyncMock()
        response = await job_service.create(job_data, authorized_pools=["maas-pool1"], is_admin=False)
        
        # Verify
        assert "created successfully" in response.detail
        mock_repo.create.assert_called_once()
        mock_producer.send_event.assert_called_once()

    
@pytest.mark.asyncio
async def test_create_job_exists(init_beanie_db, job_service, mock_repo, mock_pool_repo):
    mock_pool_repo.get.return_value = MagicMock(collector_clusters=["ocp4-col1"])
    mock_repo.get.return_value = GeneralJob(
        job_name="test-job", 
        maas_pool="maas-pool1", 
        collector_cluster="ocp4-col1",
        job_type=JobType.GENERAL,
        targets=["t1"]
    )
    
    job_data = GeneralJobCreate(
        job_name="test-job",
        maas_pool="maas-pool1",
        collector_cluster="ocp4-col1",
        job_type=JobType.GENERAL,
        targets=["localhost:9090"]
    )
    
    with pytest.raises(JobNameExistsError):
        await job_service.create(job_data, authorized_pools=["maas-pool1"], is_admin=False)
